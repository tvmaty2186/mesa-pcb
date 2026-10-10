# Mesa PCB: contexto para Claude

Este archivo es para que cualquier sesión de Claude retome el proyecto sin empezar de cero. **Leelo completo antes de tocar código.**

Última actualización: 10/10/2026 (asistente con IA).

## Dónde está todo

- Repositorio: https://github.com/tvmaty2186/mesa-pcb (rama `main`; los cambios se suben directo a `main`).
- Página publicada (GitHub Pages): https://tvmaty2186.github.io/mesa-pcb/ — tarda 1 o 2 minutos en actualizarse después de cada push. Hay que recargar con Ctrl+F5.
- Cuentas y proyectos en la nube: Firebase, proyecto `mesa-pcb` (plan Spark, gratis). Ya está conectado y funcionando.

## Próximos pasos (en este orden)

1. **Pads más grandes donde sobre lugar** (más fáciles de soldar y agujerear a mano), **zonas prohibidas** (áreas donde no pasa ninguna pista, por ejemplo debajo de un disipador) y **varias alternativas de ruteo** para elegir.
2. **Asistente con IA: hecho el código (10/10/2026), falta activarlo.** Matías tiene que hacer `docs/configurar_asistente.md`: plan Blaze, clave de Anthropic como secreto y subir `functions/` desde Google Cloud Shell. Después: **cobrar con Mercado Pago y paquetes de créditos** (decidido). Plan:
   - Una función crea una preferencia de Checkout Pro → el usuario paga → el webhook de Mercado Pago avisa a otra función, que suma `creditos` en `users/{uid}` (solo el servidor los cambia).
   - Falta que Matías pase las credenciales de producción de Mercado Pago (como secreto del servidor, nunca en el chat) y decida precios y paquetes.
3. **Publicidad (en curso, 10/10/2026):** el código ya está (`publicidad.js` con `ADS_CONFIG`, `adsInit`, `rewardedAd`, `withAd`); faltan los datos de las cuentas. Pasos y dónde sale cada dato: `docs/configurar_publicidad.md`. Banner con AdSense; pantalla completa con Ad Manager, anuncio con recompensa (GPT `OutOfPageFormat.REWARDED`); si no hay aviso, cuenta regresiva en el espacio reservado. Requisitos de Google: dominio propio (AdSense casi nunca aprueba `github.io`). **Matías no quiere comprar dominio (10/10/2026)**: se le propuso probar AdSense igual con un repositorio `tvmaty2186.github.io` (para el `ads.txt` en la raíz), sumar colaboraciones (Cafecito o Mercado Pago) y un botón de afiliado "Fabricá tu placa" (JLCPCB/PCBWay), y como respaldo redes que no piden dominio (Adsterra, Monetag); falta su respuesta. Otros requisitos: política de privacidad y términos (hechos: `privacidad.html`, `terminos.html`), contenido con texto (`guia.html`), y AdSense aprobado antes de Ad Manager. Al conectar el dominio: CNAME en GitHub Pages, agregar el dominio en Firebase → Authentication → Dominios autorizados, y `ads.txt` en la raíz. El correo público de contacto es tvmaty2186@gmail.com (lo eligió Matías).

Pendientes chicos:
- "Entrada de audio lejos de la salida" al reacomodar: falta marcar en la biblioteca qué pata es entrada o salida de audio. Hoy lo puede indicar el asistente con `separados`.
- En celular la página queda más ancha que la pantalla (la barra de herramientas no entra y el navegador achica todo).

## Quién y qué

- Dueño: Matías. Técnico electrónico con casi 20 años en mantenimiento y electromecánica.
- Producto: **Mesa PCB**, un programa web para diseñar plaquetas de circuito impreso, gratis y con publicidad (banner).
- Público: **adultos** (mayores de 18). Aficionados y técnicos que hacen placas en casa.
- Gran diferencia con KiCad o EasyEDA: **cero librerías para descargar**. Las huellas se calculan desde encapsulados estándar y vienen en una biblioteca propia.
- A futuro: asistente con IA, modo esquema y 3D.

## Cómo hablar con Matías

- Castellano rioplatense (voseo). Respuestas **cortas, claras y en orden**. Frases simples.
- Prefiere dictar y escuchar: evitá bloques largos de texto y tecnicismos sin explicar.
- Al terminar un cambio: decí qué cambió en pocas líneas, sin repetir todo lo hecho.
- Si algo no se puede o tiene un límite, decilo de entrada y con honestidad.
- Cuidá su crédito: trabajo agrupado, sin vueltas de más.

## Reglas de fabricación (no negociables)

Placas de **una sola cara**, componentes de **agujero pasante** (nada de SMD), hechas con **planchado y percloruro**.

| Regla | Valor |
|---|---|
| Separación mínima entre cobre | **0,6 mm** (la biblioteca lo verifica sola) |
| Ancho de pista de señal | 0,8 mm por defecto, nunca menos de 0,5 mm |
| Potencia (IPC-2221 + margen casero) | 1 A → 1 mm · 2 A → 1,5 mm · 3 A → 2 mm |
| Borde de placa | 2 mm libres |
| **Esquinas** | **Nunca a 90°. Siempre quiebres de 45°** (una esquina de 90° = dos de 45°). Prohibidos los ángulos agudos. Rige para pistas manuales, autorruteador y uniones en T. Decisión de Matías. |
| Pads | Ovalados donde haga falta para mantener 0,6 mm. Pad 1 cuadrado. |
| Entre patas de un DIP | No entra ninguna pista (quedan 0,74 mm). Entre filas sí, hasta 3. |
| Grilla | 2,54 mm para enganchar componentes (1,27 opcional). Líneas guía de 1 cm aparte. |
| Plano de masa | A 0,8 mm de todo; sin tiras de menos de 0,8 mm ni pedazos de menos de 4 mm². |

Detalle y fuentes en `docs/investigacion_ruteo.md`.

## Interfaz (decisiones de Matías)

- Tablero casi a pantalla completa. Líneas de 1 cm, grilla fina, reglas y enganche: **cada una se prende y apaga**.
- Menús clásicos arriba (Archivo, Editar, Ver, Herramientas, Preferencias, Ayuda). A la derecha del menú, el botón de la **cuenta de Google**.
- **Barra de herramientas solo con íconos**: el nombre aparece al pasar el mouse (`title`), nunca como texto visible. **A la derecha**: un ícono por vista (lado componentes, lado cobre, hoja para planchar).
- La función "tamaño real 1:1" en pantalla **se sacó a pedido de Matías** (complicada, no suma): **no volver a agregarla**. La escala real va en la impresión.
- **Panel izquierdo solo con la biblioteca** (por categorías, tipo acordeón) y una vista previa abajo. Ancho ajustable arrastrando el borde. Se oculta y se muestra sin mover el dibujo.
- Se arrastra al tablero **desde la lista o desde la vista previa**, con fantasma enganchado a la grilla.
- **Barra de propiedades fina (32 px) arriba, dentro de la mesa**, al seleccionar algo. Nunca un panel lateral. Botones con ícono. El dibujo no se mueve cuando aparece.
- **Clic derecho** abre un menú con las acciones de lo que está debajo (`showCtx` y el listener `contextmenu`):
  - componente: rotar, candado, desconectar, duplicar, borrar;
  - pista: ancho, candado, borrar (si el clic cae justo sobre el cobre de una pista, gana la pista aunque esté debajo de un componente);
  - conexión: corriente 1/2/3 A, invertir, borrar;
  - selección o grupo: rotar todo, agrupar/desagrupar, candado, desconectar, duplicar, borrar;
  - agujero: diámetro, volver a la esquina, borrar;
  - contorno: ajustar al mínimo, agujeros, plano, borrar;
  - marca roja de la revisión de reglas: explicación y arreglo automático;
  - tablero vacío: autorruteador, reglas, plano, alivio térmico, rellenar, lágrimas, agujeros, agregar agujero.
- **Sin textos de ayuda automáticos** (nada de carteles que expliquen cómo usar una herramienta). Solo avisos cortos de confirmación.
- **Sin barra de estado** abajo.
- **Franja publicitaria reservada abajo de todo**: 468 × 60 en computadora, 320 × 50 en celular (comentario en `index.html` donde va el código del aviso).
- **Publicidad de pantalla completa antes de guardar, imprimir (una o varias), exportar (PDF, Gerber, diseño), importar y autorrutear** (también el rerruteo de la revisión de reglas), pedido de Matías (`withAd`, `AD_SECONDS`=5). Va después del pedido de cuenta: primero "Entrá con Google", después el aviso, después la acción. Cuenta regresiva "Podés seguir en N" → "Continuar"; la ✕ cancela la acción. Con `ADS_CONFIG.rewardedUnit` pide un **anuncio con recompensa de Ad Manager** ("Ver aviso y seguir"; si lo cierra antes, se cancela); sin dato o sin aviso, queda el espacio reservado con la cuenta regresiva (AdSense no permite obligar a ver un aviso para seguir).
- **Botón "Asistente con IA"** abajo del panel izquierdo, en lugar de "Colocar en el tablero" (para colocar: arrastrar, o doble clic en la lista). Abre la ventana del asistente (`aiDlg`): flotante abajo a la derecha de la mesa (en celular, abajo de todo), no mueve el dibujo. Sin publicidad (es pago).
- **Botón dividido "Pista ▾"**: se elige Pista o Conectar con la flechita.
- Tres vistas: componentes (arriba), cobre visto de abajo (espejado), hoja para planchar (negro, **sin espejar** porque el cobre va abajo).
- Cuadros de opciones con el estilo del autorruteador: bloques con título, interruptores para sí/no, botones unidos para pocas opciones, listas para muchas.

## Qué hace hoy (todo en `index.html`)

**Biblioteca y mesa**
- 161 componentes y 97 encapsulados (resistencias, capacitores, diodos, LEDs, transistores TO-92/TO-126/TO-220, reguladores, integrados DIP, microcontroladores, amplificadores de audio, relé, jack, borneras…).
- Colocar, mover, rotar (R), duplicar, borrar, deshacer/rehacer, contorno (en **cm con decimales**), medir, tema claro/oscuro.
- **No se suelta nada encima de otro**: ni un componente sobre otro o sobre la zona de un agujero, ni un agujero sobre un componente u otro agujero. El fantasma se pinta en rojo; si se suelta igual, vuelve (`compBlocked`, `holeBlocked`). Duplicar busca lugar libre.
- **Candado** en componentes y pistas: lo fijo no se mueve, no se rota ni se borra.
- **Selección múltiple y grupos**: el rectángulo toma componentes, pistas, puentes, agujeros movidos a mano y el **contorno** si lo encierra entero (`sel`, `selT`, `selJ`, `selH`, `selO`; `sel.clear()` limpia todo). Lo seleccionado se mueve, rota (alrededor de un punto de grilla), duplica, fija y borra junto. Agrupar con clic derecho o Ctrl+G (Ctrl+Shift+G desagrupa); el grupo se guarda como `group` en cada elemento y al tocar cualquier parte se selecciona entero. Mover o rotar un grupo con contorno lleva agujeros y plano juntos. Las pistas que llegan al grupo desde afuera no se mueven.

**Conexiones y pistas**
- Conectar pad con pad (línea punteada). **Una pista que une pads vale como Conectar** (`linksFromTracks`). Si une dos conexiones distintas no las mezcla: avisa "corto".
- Pista manual con quiebres de 45° automáticos (`path45`, `chamfer`).
- **Ancho por corriente** en cada conexión (`link.amps` → 1 / 1,5 / 2 mm).

**Revisión de reglas** (tecla D, `runDrc`)
- Marca en rojo: corto, separación < 0,6 mm, pista < 0,5 mm, cobre a menos de 2 mm del borde o en la zona de un agujero, esquinas fuera de la regla de 45°, conexiones sin rutear.
- **Clic derecho sobre la marca**: explica en palabras simples (`DRC_WHY`) y ofrece arreglarlo (`drcFixes`): ancho a 0,8 mm, rehacer con 45°, rutear por otro lado, correr un componente (`moveCompFix`), agrandar el contorno, quitar agujeros, rutear lo que falta. Nunca toca lo que tiene candado.

**Autorruteador** (tecla A, `autoroute`; cuadro `routeDlg`; opciones en `prefs.route`)
- Grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo giros de 45°. Las pistas salen y llegan a un pad (sin uniones en T). Varias pasadas de arrancar y rerutear (Rápido/Normal/A fondo = 4/12/30).
- Bloques del cuadro: **Pistas** (ancho de señal y de alimentación/masa, separación 0,8 cómoda o 0,6, primero alimentación y masa), **Puentes de alambre** (opcional; máximo 1/2/3/5; largo 7,62/10,16; nunca debajo de un componente; `doc.jumpers`), **Placa** (reacomodar componentes, tamaño: no tocar / mínimo / estándar 5×5 a 15×20 cm, agujeros de fijación), **Terminación** (lágrimas, plano de masa, conservar pistas dibujadas o solo las fijas, esfuerzo).
- Detecta alimentación y masa por nombre de pata (GND/VCC/VDD/VSS/V+/V−) y por la entrada/salida de reguladores.
- **Reacomodar** (`placeComps`): recocido simulado en grilla de 2,54 mm; respeta candados; cuida largo de conexiones, cruces, superposición, desacople junto al integrado, reguladores y borneras al borde.

**Cobre extra**
- **Lágrimas** en los pads (`tearShapes`), solo si respetan 0,6 mm.
- **Plano de masa** (`planeGeo` decide qué queda; `drawPlane` lo dibuja liso). Atado al contorno, hasta 2 mm del borde. **Rellena también los espacios vacíos** como cobre suelto para ahorrar percloruro (`doc.plane.fill`). **Alivio térmico** en las patas de masa: 0,6 mm libres y 4 rayos de 0,8 mm, solo los que llegan al plano (`doc.plane.thermal`). Sigue a las pistas en vivo mientras se arrastra. Sin GND, igual rellena (`doc.plane.key=null`).
- **Agujeros de fijación** opcionales: 3 mm por defecto, en las esquinas a 4 mm del borde, sin cobre hasta 2 mm alrededor. Los de esquina siguen al contorno; se arrastran y se les cambia el diámetro con clic derecho (`doc.holes`).

**Imprimir y exportar** (menú Archivo)
- **Imprimir hoja para planchar** (Ctrl+P, `printSheet`): tamaño real en A4, ~600 ppp, con una **barra de 5 cm** para comprobar la escala (imprimir al 100 %).
- **Imprimir varias por hoja…** (`multiDlg`): copias 2/4/6/8 o todas las que entren, separación 2/5/10 mm; elige solo A4 parada o acostada y placa derecha o girada (`sheetLayout`). Imprime o exporta PDF.
- **Exportar PDF 1:1** (`exportPdf`, `buildPdf`: PDF armado a mano, sin librerías).
- **Exportar Gerber** (`exportGerber`): ZIP con cobre `.gbl` (plano y alivios incluidos), contorno `.gko` y agujeros `.drl`.
- **Exportar diseño** a `.json` (descargar o copiar) e importarlo.

**Asistente con IA** (`aiDlg`, `aiSend`, `aiApply`; servidor en `functions/`)
- Chat con texto, **dictado por voz** (es-AR, si el navegador lo permite), **imágenes y PDF** (adjuntar, pegar o arrastrar; las imágenes se achican a 1568 px) y **links** (el servidor baja el contenido; los de GitHub van a la versión cruda; no entra a redes internas).
- Atajos: Autorrutear con IA, Revisar el diseño, Explicar lo seleccionado.
- La IA **no dibuja**: devuelve JSON (`functions/nucleo.js`, `ESQUEMA`) con `respuesta`, `pregunta` (con opciones), `agregar` (nombre exacto de la biblioteca), `redes` (patas `REF.NÚMERO`, `amperes`), `desconectar`, `quitar`, `valores`, `contorno`, `ruteo` y `marcar`. La página muestra el plan en una línea con **Aplicar / Descartar**; aplicar es un solo paso de deshacer (`aiEdit`). Lo que no existe (pieza fuera de la biblioteca, pata inválida) no se aplica y se avisa.
- **Autorruteo asistido** (`aiRoute`): la IA indica reacomodar, tamaño, `juntos` / `separados` / `borde` (entran al costo de `placeComps` como `o.near`, `o.apart`, `o.edge`), `primero` (redes que se rutean antes, `opt.first` en `autoroute`), puentes, anchos y plano. Si quedan conexiones sin rutear prueba variantes sin gastar tokens (más esfuerzo, otras semillas de acomodo `o.seed`, un puente más si se permiten) y se queda con la mejor.
- Instrucciones de honestidad en el servidor: no inventar piezas, valores ni patas; si duda, pregunta con opciones; si la pieza no tiene tabla de pines, no supone el orden.
- **Ahorro de tokens**: instrucciones + biblioteca resumida (`functions/catalogo.txt`, la genera `build_lib.py`) en caché; el diseño va como texto corto (`aiDesign`); el historial (8 mensajes) solo como texto; esfuerzo `low` para preguntas y `medium` con archivos o ruteo; salida estructurada.
- **Créditos** en `users/{uid}`: `gratisMes`, `gratisUsadas` (5 gratis por mes, `GRATIS_POR_MES`) y `creditos` (comprados). Se descuentan antes de llamar a la IA y se devuelven si falla. Costo: 1 por mensaje, +1 con imágenes, +1 cada 10 páginas de PDF, +1 con link. Consumo de tokens en `users/{uid}/consumo`. **Consultas ilimitadas** para las cuentas de `ILIMITADOS` en `nucleo.js` (hoy tvmaty2186@gmail.com, pedido de Matías para probar); no descuentan nada y la ventana dice "Consultas ilimitadas". Funciones: `asistente` y `saldo` (llamables, exigen cuenta).
- Modelo: `claude-opus-5-5` (`MODELO` en `nucleo.js`), con `fallbacks: "default"`.

**Cuentas con Google** (Firebase, `firebase-config.js`)
- Botón **Entrar con Google** arriba a la derecha; con sesión muestra foto o inicial, nombre y menú (Mis proyectos, Guardar, Salir).
- **Sin cuenta solo se dibuja y diseña**: guardar, abrir, imprimir y exportar piden entrar (`needAccount`).
- Proyectos en Firestore `users/{uid}/projects/{id}` = `{name, data (JSON del diseño), comps, updated}` (`cloudSave`, `cloudOpen`). `doc.cloudId` recuerda el proyecto abierto. Cada usuario ve solo los suyos (reglas en `firestore.rules`).
- Los diseños viejos guardados en el navegador aparecen en Mis proyectos para pasarlos a la cuenta.
- Si `FIREBASE_CONFIG` es `null`, la página funciona sin cuentas y guarda en el navegador.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La mesa de trabajo (todo en un solo archivo: HTML, CSS y JS). |
| `huellas.html` | Buscador de huellas: escribís los componentes en castellano y dibuja cada huella. |
| `biblioteca/build_lib.py` | **Fuente de verdad de la biblioteca.** Genera `componentes.json` y `componentes.js`. Verifica pines por huella y separación mínima. |
| `biblioteca/componentes.json` / `.js` | Biblioteca generada. **No editar a mano**: cambiar `build_lib.py` y correr `python3 build_lib.py` dentro de `biblioteca/`. `componentes.js` existe para abrir la página con doble clic (sin servidor). |
| `firebase-config.js` | Datos del proyecto Firebase `mesa-pcb` (no son secretos). |
| `publicidad.js` | Datos de AdSense y Ad Manager (`ADS_CONFIG`). En `null` = espacios reservados. |
| `docs/configurar_publicidad.md` | Cómo conectar la publicidad, paso a paso. |
| `firestore.rules` | Reglas de seguridad de Firestore. `users/{uid}` (créditos) solo se lee; lo cambia el servidor. Se publican con `firebase deploy --only firestore:rules`. |
| `functions/` | Servidor del asistente (Firebase Functions): `index.js` (cuenta, créditos, llamada a Claude), `nucleo.js` (instrucciones, formato de respuesta, validación, links; se prueba con `node prueba.js`), `catalogo.txt` (generado). |
| `firebase.json`, `.firebaserc` | Configuración para subir el servidor y las reglas. |
| `docs/configurar_asistente.md` | Cómo activar el asistente (Blaze, clave de Anthropic, subir el servidor) y cuánto cuesta. |
| `docs/configurar_firebase.md` | Cómo se configuró Firebase, paso a paso. |
| `docs/investigacion_ruteo.md` | Investigación de reglas y algoritmos de ruteo, con fuentes. |
| `guia.html`, `privacidad.html`, `terminos.html` | Guía para hacer la plaqueta, política de privacidad y términos de uso (los pide Google para la publicidad). Enlazadas desde el menú Ayuda. |
| `README.md` | Presentación corta para quien entra al repositorio. |
| `PASOS.md` | Cómo seguir trabajando con Claude en la nube. |

## Notas técnicas

- Unidades internas: milímetros. Origen arriba a la izquierda, Y hacia abajo. El contorno se muestra en cm.
- Documento (`docData`, `docFrom`): `{name, comps:[{id,ref,name,enc,val,x,y,rot,lock?,group?}], outline:{x,y,w,h,group?}, tracks:[{id,pts:[[x,y]...],w,lock?,group?}], links:[{id,a:"compId:pad",b:"compId:pad",amps?}], jumpers:[{id,a,b,group?}], tears, plane:{key,thermal,fill}|null, holes:[{id,corner,x,y,d,group?}]}`. En el navegador se guarda la copia de trabajo en `localStorage` (`pcb.actual`).
- Rotación en pasos de 90° (`rot` 0 a 3). El pin 1 se engancha a la grilla.
- Las funciones `path45` y `chamfer` aplican la regla de 45°: no las saltees en código nuevo de pistas.
- `changed()` sube `geoVer` y marca la revisión de reglas para recalcular; plano y lágrimas se cachean por `geoVer`.
- Antes de agregar un componente nuevo: verificá medidas en la hoja de datos o en las huellas oficiales de KiCad. Si el orden de patas no está confirmado, no lo inventes: dejalo sin tabla de pines y avisá.

## Cómo probar

- En la nube hay Chromium: Playwright con `executablePath:'/opt/pw-browsers/chromium'`, abriendo `file:///…/index.html`. Probar con el ejemplo (`example()`), revisar `runDrc()` y sacar capturas.
- En el entorno de Claude puede no haber salida a `gstatic.com` (Firebase): para probar, bajar `firebase@10.12.2` con npm y servir los `firebase-*-compat.js` con `page.route`.
- El link de prueba de Claude (artifact) no deja descargar archivos ni entrar con Google: para eso usar la página de GitHub Pages.
