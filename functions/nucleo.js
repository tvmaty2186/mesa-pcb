// Lógica del asistente con IA, separada de Firebase para poder probarla sola.
// Qué arma: el pedido a la API de Claude (instrucciones fijas + biblioteca, cacheadas; el diseño y el
// pedido del usuario van aparte), la validación de lo que manda la página y el costo en créditos.
const fs = require('fs');
const path = require('path');
const dns = require('dns').promises;
const net = require('net');

// ---------- ajustes (Matías puede cambiarlos acá) ----------
const MODELO = 'claude-opus-5-5';
const GRATIS_POR_MES = 5;          // consultas gratis por mes para cada usuario mientras no se cobra
const MAX_TOKENS = 16000;
const LIM = {
  texto: 4000,                     // caracteres del pedido
  diseno: 30000,                   // caracteres del resumen del diseño
  historial: 8,                    // mensajes anteriores que se reenvían (solo texto)
  histTexto: 2000,
  adjuntos: 4,
  base64Total: 14_000_000,         // ~10 MB de archivos
  pdfPaginas: 30,
  linkBytes: 6_000_000,
  linkTexto: 60000,
};
const TIPOS_IMG = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif']);

// ---------- instrucciones fijas (se cachean: no cambian entre pedidos) ----------
const CATALOGO = fs.readFileSync(path.join(__dirname, 'catalogo.txt'), 'utf8').trim();
const SISTEMA = `Sos el asistente de Mesa PCB, un programa web para diseñar plaquetas de UNA sola cara, con componentes de agujero pasante, que el usuario hace en casa con planchado y percloruro. Hablás en castellano rioplatense (voseo), con frases cortas y simples. El público son aficionados y técnicos.

HONESTIDAD (lo más importante)
- No inventes nada: ni componentes, ni valores, ni patas, ni conexiones.
- Si algo no se lee bien en una imagen o un PDF, si falta un dato o si hay más de una interpretación posible, no hagas cambios: preguntá con "pregunta" (con 2 a 4 opciones cortas cuando se pueda).
- Si un componente no está en la BIBLIOTECA, decilo. Proponé otro solo si es equivalente de verdad (mismo encapsulado y mismo orden de patas) y aclaralo.
- Si una pieza de la biblioteca no tiene los nombres de sus patas, no supongas el orden: preguntá o decí que hay que confirmarlo con la hoja de datos.
- Si no sabés algo, decí que no lo sabés.

RESPUESTA (siempre el JSON pedido; no pongas los campos que no uses)
- respuesta: lo que le decís al usuario. Corto (hasta 4 frases), sin markdown. Si hacés cambios, resumilos en una frase.
- pregunta: cuando necesitás un dato antes de hacer cambios.
- agregar: componentes nuevos. "parte" = el nombre EXACTO de la biblioteca. "ref" = una referencia que no exista todavía (R1, C1, D1, LED1, Q1, U1, J1, K1, RV1, SW1, Y1…). "valor" cuando corresponde ("10 kΩ", "100 nF", "NE555"). "pines" solo para "Tira de pines". "x", "y" (mm desde la esquina de arriba a la izquierda de la placa) y "rot" (0 a 3, pasos de 90°) solo si copiás una placa de una foto; si no, no los pongas.
- redes: cada red es una lista de patas unidas, con el formato REF.NÚMERO (por ejemplo "U1.3"). La pata 1 es la primera de la lista de la biblioteca. "nombre" opcional (GND, VCC, SALIDA…). "amperes" (1, 2 o 3) solo en redes con corriente fuerte.
- desconectar: patas (REF.NÚMERO) a las que hay que quitarles las conexiones.
- quitar: referencias a borrar. valores: cambios de valor.
- contorno: tamaño de la placa en mm, si lo piden o si copiás una placa.
- ruteo: para reacomodar y rutear con tus indicaciones (ver AUTORRUTEO).
- marcar: referencias para resaltar en la mesa cuando sugerís o explicás algo.

AUTORRUTEO ASISTIDO
El programa tiene un autorruteador (una cara, quiebres de 45°) y un reacomodador de componentes. Vos no dibujás pistas: das indicaciones en "ruteo".
- reacomodar: true si conviene mover componentes. tamano: "none" (no tocar la placa) o "min" (achicarla al final).
- juntos: pares de referencias que deben quedar cerca (desacople junto a la pata de alimentación del integrado, cristal junto al micro, resistencia de base junto al transistor…).
- separados: pares que conviene alejar (entrada y salida de audio, potencia y señal chica, 220 V y baja tensión).
- borde: referencias que van al borde (borneras, jacks, conectores, reguladores con disipador).
- primero: una pata de cada red que conviene rutear antes (masa y alimentación, después lo crítico).
- puentes: máximo de puentes de alambre (0 si no hacen falta).
- ancho_senal y ancho_potencia en mm: señal 0,8 (nunca menos de 0,5); 1 A → 1; 2 A → 1,5; 3 A → 2.
- plano: true para plano de masa.
Marcá también con "amperes" las redes de potencia que lo necesiten. En "respuesta" explicá en una o dos frases qué priorizaste.

REGLAS DE FABRICACIÓN
Una cara, agujero pasante, nada de SMD. Separación mínima entre cobre 0,6 mm. Borde libre 2 mm. Esquinas siempre a 45°. Entre patas de un DIP no pasa ninguna pista.

ESQUEMÁTICOS, FOTOS, PDF Y LINKS
- Esquemático: identificá cada componente, buscá su parte en la biblioteca y armá las redes. Usá el número de pata de la biblioteca: en los esquemas el orden del dibujo no es el físico.
- Foto de una placa: si se ve el lado del cobre, está espejada respecto del lado de los componentes; si no está claro de qué lado es, preguntá. Las posiciones son aproximadas. Las pistas no se copian una por una: se arman las redes y después se rutea.
- Lista de componentes: agregalos sin conectar, salvo que diga cómo van.
- Link: usá solo el contenido que viene en el mensaje. Si no alcanza para entender el circuito, decilo.
- Un pedido grande se resuelve entero en una sola respuesta.

El diseño actual viene en cada mensaje entre [DISEÑO] y [FIN].

BIBLIOTECA (nombre|categoría|encapsulado|cantidad de patas|nombre de cada pata en orden, si se conoce)
${CATALOGO}`;

// ---------- formato de la respuesta (salida estructurada) ----------
const S = { type: 'string' }, N = { type: 'number' }, I = { type: 'integer' }, B = { type: 'boolean' };
const lista = items => ({ type: 'array', items });
const obj = (properties, required) => ({ type: 'object', additionalProperties: false, required, properties });
const ESQUEMA = obj({
  respuesta: S,
  pregunta: obj({ texto: S, opciones: lista(S) }, ['texto', 'opciones']),
  agregar: lista(obj({ ref: S, parte: S, valor: S, pines: I, x: N, y: N, rot: I }, ['ref', 'parte'])),
  redes: lista(obj({ nombre: S, patas: lista(S), amperes: { type: 'integer', enum: [1, 2, 3] } }, ['patas'])),
  desconectar: lista(S),
  quitar: lista(S),
  valores: lista(obj({ ref: S, valor: S }, ['ref', 'valor'])),
  contorno: obj({ ancho: N, alto: N }, ['ancho', 'alto']),
  ruteo: obj({
    reacomodar: B, tamano: { type: 'string', enum: ['none', 'min'] },
    juntos: lista(lista(S)), separados: lista(lista(S)), borde: lista(S), primero: lista(S),
    puentes: I, ancho_senal: N, ancho_potencia: N, plano: B,
  }, ['reacomodar']),
  marcar: lista(S),
}, ['respuesta']);

// ---------- validación de lo que manda la página ----------
class ErrorPedido extends Error {}
const esTexto = (v, max) => typeof v === 'string' && v.length <= max;

function validar(d) {
  if (!d || typeof d !== 'object') throw new ErrorPedido('Pedido vacío.');
  const texto = (d.texto || '').trim();
  if (!esTexto(texto, LIM.texto)) throw new ErrorPedido('El mensaje es demasiado largo.');
  if (!esTexto(d.diseno || '', LIM.diseno)) throw new ErrorPedido('El diseño es demasiado grande para el asistente.');
  const historial = Array.isArray(d.historial) ? d.historial.slice(-LIM.historial) : [];
  for (const m of historial) {
    if (!m || !['user', 'assistant'].includes(m.rol) || !esTexto(m.texto, LIM.histTexto)) throw new ErrorPedido('Historial inválido.');
  }
  const adjuntos = Array.isArray(d.adjuntos) ? d.adjuntos : [];
  if (adjuntos.length > LIM.adjuntos) throw new ErrorPedido(`Podés mandar hasta ${LIM.adjuntos} archivos por mensaje.`);
  let total = 0, paginas = 0, imagenes = 0;
  for (const a of adjuntos) {
    if (!a || typeof a.datos !== 'string' || !/^[A-Za-z0-9+/=]+$/.test(a.datos)) throw new ErrorPedido('Archivo inválido.');
    total += a.datos.length;
    if (a.tipo === 'application/pdf') {
      const n = contarPaginas(a.datos);
      if (n > LIM.pdfPaginas) throw new ErrorPedido(`El PDF tiene ${n} páginas. Mandá solo las que hacen falta (hasta ${LIM.pdfPaginas}).`);
      paginas += Math.max(1, n);
    } else if (TIPOS_IMG.has(a.tipo)) imagenes++;
    else throw new ErrorPedido('Solo se aceptan imágenes (JPG, PNG, WEBP) y PDF.');
  }
  if (total > LIM.base64Total) throw new ErrorPedido('Los archivos son muy pesados (máximo 10 MB en total).');
  const link = typeof d.link === 'string' && d.link ? d.link.trim() : null;
  if (link && !esTexto(link, 2000)) throw new ErrorPedido('El link es demasiado largo.');
  if (!texto && !adjuntos.length && !link) throw new ErrorPedido('Escribí qué necesitás.');
  return { texto, diseno: d.diseno || '', historial, adjuntos, link, paginas, imagenes };
}

// cantidad de páginas de un PDF (aproximada, contando los objetos de página)
function contarPaginas(b64) {
  const s = Buffer.from(b64, 'base64').toString('latin1');
  return (s.match(/\/Type\s*\/Page(?![s\w])/g) || []).length;
}

// créditos que cuesta un pedido: 1 por mensaje, +1 si hay imágenes, +1 por cada 10 páginas de PDF, +1 por link
function costo(p) {
  return 1 + (p.imagenes ? 1 : 0) + Math.ceil(p.paginas / 10) + (p.link ? 1 : 0);
}

// ---------- links: el servidor baja el contenido (con cuidado de no tocar redes internas) ----------
function ipPrivada(ip) {
  if (net.isIPv4(ip)) {
    const [a, b] = ip.split('.').map(Number);
    return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && b === 168) || (a === 100 && b >= 64 && b <= 127) || a >= 224;
  }
  const s = ip.toLowerCase();
  if (s.startsWith('::ffff:')) return ipPrivada(s.slice(7));
  return s === '::' || s === '::1' || s.startsWith('fc') || s.startsWith('fd') || s.startsWith('fe80');
}
async function hostSeguro(host) {
  if (/^(localhost|metadata(\.google\.internal)?)$/i.test(host) || host.endsWith('.internal') || host.endsWith('.local')) return false;
  const ips = net.isIP(host) ? [{ address: host }] : await dns.lookup(host, { all: true });
  return ips.length > 0 && ips.every(x => !ipPrivada(x.address));
}
// links de GitHub a la versión "cruda" del archivo
function linkDirecto(u) {
  const m = u.match(/^https:\/\/github\.com\/([^/]+)\/([^/]+)\/blob\/(.+)$/);
  return m ? `https://raw.githubusercontent.com/${m[1]}/${m[2]}/${m[3]}` : u;
}
function htmlATexto(h) {
  return h.replace(/<(script|style|noscript|svg)[\s\S]*?<\/\1>/gi, ' ').replace(/<br\s*\/?>|<\/(p|div|li|tr|h\d)>/gi, '\n')
    .replace(/<[^>]+>/g, ' ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/[ \t]+/g, ' ').replace(/\n\s*\n+/g, '\n').trim();
}
// devuelve un bloque de contenido para Claude (texto, imagen o PDF)
async function traerLink(u, fetchFn = fetch) {
  let url;
  try { url = new URL(linkDirecto(u)); } catch { throw new ErrorPedido('Ese link no es válido.'); }
  for (let salto = 0; salto < 4; salto++) {
    if (!/^https?:$/.test(url.protocol)) throw new ErrorPedido('Solo se aceptan links http o https.');
    if (!(await hostSeguro(url.hostname))) throw new ErrorPedido('No puedo abrir ese link.');
    let r;
    try { r = await fetchFn(url, { redirect: 'manual', signal: AbortSignal.timeout(10000), headers: { 'user-agent': 'MesaPCB/1.0' } }); }
    catch { throw new ErrorPedido('No pude abrir el link (no responde).'); }
    if (r.status >= 300 && r.status < 400 && r.headers.get('location')) { url = new URL(r.headers.get('location'), url); continue; }
    if (!r.ok) throw new ErrorPedido(`No pude abrir el link (error ${r.status}).`);
    const tipo = (r.headers.get('content-type') || '').split(';')[0].trim().toLowerCase();
    const buf = Buffer.from(await r.arrayBuffer());
    if (buf.length > LIM.linkBytes) throw new ErrorPedido('El archivo del link es demasiado grande.');
    if (tipo === 'application/pdf') {
      const b64 = buf.toString('base64'), n = contarPaginas(b64);
      if (n > LIM.pdfPaginas) throw new ErrorPedido(`El PDF del link tiene ${n} páginas (máximo ${LIM.pdfPaginas}).`);
      return { tipo: 'pdf', paginas: n, bloque: { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: b64 } } };
    }
    if (TIPOS_IMG.has(tipo)) return { tipo: 'imagen', bloque: { type: 'image', source: { type: 'base64', media_type: tipo, data: buf.toString('base64') } } };
    let t = buf.toString('utf8');
    if (tipo.includes('html')) t = htmlATexto(t);
    if (t.length < 200) throw new ErrorPedido('Ese link no tiene contenido que se pueda leer (puede que la página necesite abrirse en un navegador). Probá con una captura o un PDF.');
    return { tipo: 'texto', bloque: { type: 'text', text: `[CONTENIDO DEL LINK ${url.href}]\n${t.slice(0, LIM.linkTexto)}\n[FIN DEL LINK]` } };
  }
  throw new ErrorPedido('El link redirige demasiadas veces.');
}

// ---------- pedido a la API ----------
function armarPedido(p, bloqueLink) {
  const contenido = [];
  for (const a of p.adjuntos) {
    contenido.push(a.tipo === 'application/pdf'
      ? { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: a.datos } }
      : { type: 'image', source: { type: 'base64', media_type: a.tipo, data: a.datos } });
  }
  if (bloqueLink) contenido.push(bloqueLink);
  contenido.push({ type: 'text', text: `[DISEÑO]\n${p.diseno || 'Mesa vacía.'}\n[FIN]\n\n${p.texto || 'Mirá lo que te mandé.'}` });
  // el historial va solo como texto: las imágenes viejas no se reenvían (ahorra tokens)
  const hist = p.historial.map(m => ({ role: m.rol, content: m.texto }));
  while (hist.length && hist[0].role !== 'user') hist.shift();
  const pesado = p.adjuntos.length || bloqueLink || /\b(rute|autorrut|reacomod)/i.test(p.texto);
  return {
    model: MODELO,
    max_tokens: MAX_TOKENS,
    betas: ['server-side-fallback-2026-07-01'],
    fallbacks: 'default',
    output_config: { effort: pesado ? 'medium' : 'low', format: { type: 'json_schema', schema: ESQUEMA } },
    system: [{ type: 'text', text: SISTEMA, cache_control: { type: 'ephemeral' } }],
    messages: [...hist, { role: 'user', content: contenido }],
  };
}

// lee la respuesta de la API; devuelve {ok, r} o {ok:false, motivo}
function leerRespuesta(msg) {
  if (msg.stop_reason === 'refusal') return { ok: false, motivo: 'No puedo ayudarte con ese pedido.' };
  if (msg.stop_reason === 'max_tokens') return { ok: false, motivo: 'El pedido es demasiado grande para una sola vez. Probá dividirlo en partes.' };
  const t = msg.content.filter(b => b.type === 'text').map(b => b.text).join('');
  try {
    const r = JSON.parse(t);
    if (typeof r.respuesta !== 'string') throw 0;
    return { ok: true, r };
  } catch { return { ok: false, motivo: 'El asistente respondió algo que no se pudo leer. Probá de nuevo.' }; }
}

// ---------- créditos ----------
const mesActual = () => new Date().toISOString().slice(0, 7);
// a partir del documento del usuario: cuántas gratis le quedan este mes y cuántos créditos pagos tiene
function saldo(d, mes = mesActual()) {
  const usadas = d && d.gratisMes === mes ? d.gratisUsadas || 0 : 0;
  return { gratis: Math.max(0, GRATIS_POR_MES - usadas), creditos: (d && d.creditos) || 0, usadas };
}
// descuenta primero de las gratis y después de los créditos; devuelve los cambios o null si no alcanza
function descontar(d, c, mes = mesActual()) {
  const s = saldo(d, mes);
  if (s.gratis + s.creditos < c) return null;
  const deGratis = Math.min(s.gratis, c), dePago = c - deGratis;
  return { cambios: { gratisMes: mes, gratisUsadas: s.usadas + deGratis, creditos: s.creditos - dePago }, deGratis, dePago };
}

module.exports = { MODELO, GRATIS_POR_MES, SISTEMA, ESQUEMA, ErrorPedido, validar, costo, contarPaginas, ipPrivada, hostSeguro, linkDirecto, htmlATexto, traerLink, armarPedido, leerRespuesta, saldo, descontar, mesActual };
