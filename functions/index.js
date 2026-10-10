// Servidor del asistente con IA (Firebase Functions). La clave de la API de Anthropic vive acá como
// secreto (ANTHROPIC_API_KEY) y nunca llega a la página. Cada pedido exige estar logueado con Google
// y descuenta créditos de users/{uid} (primero las consultas gratis del mes, después los créditos
// comprados). Solo este servidor puede cambiar los créditos: las reglas de Firestore no dejan.
const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { defineSecret } = require('firebase-functions/params');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');
const Anthropic = require('@anthropic-ai/sdk');
const N = require('./nucleo');

initializeApp();
const db = getFirestore();
const CLAVE = defineSecret('ANTHROPIC_API_KEY');

exports.asistente = onCall({ secrets: [CLAVE], timeoutSeconds: 300, memory: '512MiB', maxInstances: 10 }, async (req) => {
  if (!req.auth) throw new HttpsError('unauthenticated', 'Entrá con tu cuenta de Google para usar el asistente.');
  const uid = req.auth.uid, ref = db.doc(`users/${uid}`);
  let p;
  try { p = N.validar(req.data); } catch (e) { throw aError(e); }

  // el link se baja antes de cobrar: si no se puede abrir, no se gasta nada
  let link = null;
  if (p.link) { try { link = await N.traerLink(p.link); } catch (e) { throw aError(e); } if (link.tipo === 'pdf') p.paginas += link.paginas; }
  const c = N.costo(p);

  // reservar los créditos antes de llamar a la IA
  const libre = N.ilimitado(req.auth.token); // cuentas de prueba: no descuentan nada
  const reserva = libre ? { deGratis: 0, dePago: 0 } : await db.runTransaction(async (t) => {
    const s = await t.get(ref), d = s.exists ? s.data() : {};
    const r = N.descontar(d, c);
    if (r) t.set(ref, r.cambios, { merge: true });
    return r;
  });
  if (!reserva) {
    const s = N.saldo((await ref.get()).data());
    throw new HttpsError('resource-exhausted', 'Te quedaste sin consultas.', { saldo: s, costo: c });
  }
  const devolver = () => ref.set({ gratisUsadas: FieldValue.increment(-reserva.deGratis), creditos: FieldValue.increment(reserva.dePago) }, { merge: true });

  const client = new Anthropic({ apiKey: CLAVE.value() });
  let msg;
  try { msg = await client.beta.messages.create(N.armarPedido(p, link && link.bloque)); }
  catch (e) {
    await devolver();
    console.error('API de Claude:', e.status, e.message);
    if (e instanceof Anthropic.RateLimitError || e instanceof Anthropic.InternalServerError) throw new HttpsError('unavailable', 'El asistente está ocupado. Probá de nuevo en un rato.');
    throw new HttpsError('internal', 'No se pudo consultar al asistente.');
  }
  const r = N.leerRespuesta(msg);
  if (!r.ok) await devolver();

  // registro de consumo (para controlar cuánto cuesta cada pedido)
  const u = msg.usage || {};
  await ref.collection('consumo').add({
    fecha: FieldValue.serverTimestamp(), costo: r.ok ? c : 0, modelo: msg.model,
    entrada: u.input_tokens || 0, salida: u.output_tokens || 0,
    cacheLeida: u.cache_read_input_tokens || 0, cacheEscrita: u.cache_creation_input_tokens || 0,
  });
  if (!r.ok) throw new HttpsError('failed-precondition', r.motivo);
  return { r: r.r, costo: libre ? 0 : c, saldo: libre ? { ilimitado: true } : N.saldo((await ref.get()).data()) };
});

// saldo actual (para mostrarlo al abrir el asistente)
exports.saldo = onCall(async (req) => {
  if (!req.auth) throw new HttpsError('unauthenticated', 'Entrá con tu cuenta de Google.');
  if (N.ilimitado(req.auth.token)) return { saldo: { ilimitado: true }, gratisPorMes: N.GRATIS_POR_MES };
  return { saldo: N.saldo((await db.doc(`users/${req.auth.uid}`).get()).data()), gratisPorMes: N.GRATIS_POR_MES };
});

function aError(e) {
  if (e instanceof N.ErrorPedido) return new HttpsError('invalid-argument', e.message);
  console.error(e);
  return new HttpsError('internal', 'Error inesperado.');
}
