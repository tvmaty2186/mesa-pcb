// Pruebas rápidas de la lógica del asistente (sin llamar a la IA): node prueba.js
const assert = require('assert');
const N = require('./nucleo');
(async () => {
  // validación y costo
  assert.throws(() => N.validar({ texto: '' }), /Escribí/);
  assert.throws(() => N.validar({ texto: 'x', adjuntos: [{ tipo: 'text/html', datos: 'AAAA' }] }), /Solo se aceptan/);
  const pdf = Buffer.from('%PDF-1.4 /Type /Pages /Type /Page /Type /Page').toString('base64');
  const p = N.validar({ texto: 'copiá esto', adjuntos: [{ tipo: 'application/pdf', datos: pdf }, { tipo: 'image/jpeg', datos: 'AAAA' }] });
  assert.equal(p.paginas, 2); assert.equal(N.costo(p), 3);
  // créditos: primero gratis, después pagos; si no alcanza, null
  const mes = N.mesActual();
  assert.deepEqual(N.descontar({ gratisMes: mes, gratisUsadas: N.GRATIS_POR_MES, creditos: 1 }, 1).cambios.creditos, 0);
  assert.equal(N.descontar({ gratisMes: mes, gratisUsadas: N.GRATIS_POR_MES, creditos: 0 }, 1), null);
  assert.equal(N.saldo({ gratisMes: '2000-01', gratisUsadas: 99 }).gratis, N.GRATIS_POR_MES); // mes nuevo, gratis de nuevo
  // redes internas bloqueadas
  assert.equal(await N.hostSeguro('169.254.169.254'), false);
  assert.equal(await N.hostSeguro('localhost'), false);
  // links: redirección, HTML a texto, página vacía
  const res = (status, body, tipo, loc) => ({ status, ok: status < 300, headers: { get: k => (k === 'location' ? loc : tipo) }, arrayBuffer: async () => Buffer.from(body) });
  const html = '<html><script>x</script><p>' + 'Amplificador con TDA2030. '.repeat(20) + '</p></html>';
  let llamadas = [];
  const f = async (u) => { llamadas.push(String(u)); return String(u).endsWith('/a') ? res(302, '', '', '/b') : res(200, html, 'text/html; charset=utf-8'); };
  const b = await N.traerLink('http://93.184.216.34/a', f);
  assert.equal(b.tipo, 'texto'); assert.ok(b.bloque.text.includes('TDA2030') && !b.bloque.text.includes('<p>')); assert.equal(llamadas.length, 2);
  await assert.rejects(N.traerLink('http://93.184.216.34/c', async () => res(200, '<div id=app></div>', 'text/html')), /no tiene contenido/);
  await assert.rejects(N.traerLink('http://93.184.216.34/a', async () => res(302, '', '', 'http://127.0.0.1/x')), /No puedo abrir/);
  await assert.rejects(N.traerLink('file:///etc/passwd'), /http o https/);
  // pedido a la API
  const q = N.armarPedido(N.validar({ texto: 'autorruteá con IA', diseno: 'R1|...' }), null);
  assert.equal(q.output_config.effort, 'medium'); assert.equal(q.system[0].cache_control.type, 'ephemeral');
  // respuesta
  assert.equal(N.leerRespuesta({ stop_reason: 'end_turn', content: [{ type: 'text', text: '{"respuesta":"ok"}' }] }).r.respuesta, 'ok');
  assert.equal(N.leerRespuesta({ stop_reason: 'refusal', content: [] }).ok, false);
  console.log('Todo bien');
})().catch(e => { console.error(e); process.exit(1); });
