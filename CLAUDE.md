# Mesa PCB: contexto para Claude

Este archivo es para que cualquier sesión de Claude retome el proyecto sin empezar de cero. **Leelo completo antes de tocar código.**

Última actualización: 27/11/2026 (Mesa PCB 100 % libre).

## Dónde está todo

- Repositorio: https://github.com/tvmaty2186/mesa-pcb (rama `main`; los cambios se suben directo a `main`).
- Página publicada (GitHub Pages): https://tvmaty2186.github.io/mesa-pcb/ — tarda 1 o 2 minutos en actualizarse después de cada push. Hay que recargar con Ctrl+F5.
- Cuentas y proyectos en la nube: Firebase, proyecto `mesa-pcb` (plan Spark, gratis). Ya está conectado y funcionando.

## Próximos pasos (en este orden)

1. **Pads más grandes donde sobre lugar** (más fáciles de soldar y agujerear a mano) y **zonas prohibidas** (áreas donde no pasa ninguna pista, por ejemplo debajo de un disipador). Las alternativas de ruteo ya están (búsqueda de variantes).
   - Autorruteo en placas muy justas: con el detector LDR en 5 × 5 la búsqueda automática todavía deja islas de masa sin unir (lo mejor: 4 patas de masa sin rutear); en 7 × 6 sale completo solo. Ideas pendientes: medir "bolsillos" de masa ya en el reacomodo y reservar canales.
2. **Mesa PCB es 100 % libre (decisión de Matías, 27/11/2026):** sin publicidad, sin pagos, sin créditos y sin pedir cuenta para guardar, imprimir o exportar. Se sacaron la publicidad (`publicidad.js`, `withAd`, franja de abajo) y el asistente con IA de la página. **No volver a agregarlos** salvo que Matías lo pida. El código del servidor del asistente sigue en `functions/` (no se usa); está en el historial de git (antes del commit "Mesa PCB 100 % libre") si algún día se retoma.

Pendientes chicos:
- "Entrada de audio lejos de la salida" al reacomodar: falta marcar en la biblioteca qué pata es entrada o salida de audio. Hoy no hay forma de indicarlo (antes lo hacía el asistente con `separados`; `o.apart` sigue en `placeComps`).

## Quién y qué

- Dueño: Matías. Técnico electrónico con casi 20 años en mantenimiento y electromecánica.
- Producto: **Mesa PCB**, un programa web para diseñar plaquetas de circuito impreso, **gratis y 100 % libre** (sin publicidad ni pagos).
- Público: **adultos** (mayores de 18). Aficionados y técnicos que hacen placas en casa.
- Gran diferencia con KiCad o EasyEDA: **cero librerías para descargar**. Las huellas se calculan desde encapsulados estándar y vienen en una biblioteca propia.
- A futuro: modo esquema y 3D.

## Cómo hablar con Matías

- **Todo en castellano, siempre**: también los avisos cortos mientras se trabaja ("estoy probando…", "ya lo subo"). Matías no entiende inglés (pedido del 9/11/2026).
- Castellano rioplatense (voseo). Respuestas **cortas, claras y en orden**. Frases simples.
- Prefiere dictar y escuchar: evitá bloques largos de texto y tecnicismos sin explicar.
- Al terminar un cambio: decí qué cambió en pocas líneas, sin repetir todo lo hecho.
- Si algo no se puede o tiene un límite, decilo de entrada y con honestidad.
- Cuidá su crédito: trabajo agrupado, sin vueltas de más.
- **Informes y trabajos prácticos** (los de Thiago, E.E.S.T. N.º 2): redactar en **texto continuo**, no en viñetas ni enumeraciones (pedido de Matías, 27/11/2026). Que no parezca hecho con IA: frases simples, sin notas tipo "corrección aplicada". Normas de la escuela: Times New Roman 12, subtítulos 14, justificado, interlineado 1,5, bibliografía obligatoria, nombre del proyecto en la introducción, texto debajo de cada imagen, sin repetir información. El encabezado se completa a mano.

## Reglas de fabricación (no negociables)

Placas de **una sola cara**, componentes de **agujero pasante** (nada de SMD), hechas con **planchado y percloruro**.

| Regla | Valor |
|---|---|
| Separación mínima entre cobre | **0,6 mm** (la biblioteca lo verifica sola) |
| Ancho de pista de señal | 0,8 mm por defecto, nunca menos de 0,5 mm |
| Potencia (IPC-2221 + margen casero) | 1 A → 1 mm · 2 A → 1,5 mm · 3 A → 2 mm |
| Borde de placa | 2 mm libres |
| **Esquinas** | **Nunca a 90°. Siempre quiebres de 45°** (una esquina de 90° = dos de 45°). Prohibidos los ángulos agudos: dos pistas que salen del mismo punto (una pata, un puente o una unión) nunca forman menos de 90°; **en T (90°) sí se puede** (27/11/2026). Rige para pistas manuales, autorruteador y uniones. Decisión de Matías. |
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
- **Celular** (≤ 820 px): la página entra justa en la pantalla (`.app` con `grid-template-columns:minmax(0,1fr)`); menús y barra de herramientas se deslizan de costado, sin logo; el botón de la cuenta queda fijo a la derecha; los menús se abren con `position:fixed`.
- Abajo del panel izquierdo queda la vista previa (para colocar: arrastrar, o doble clic en la lista).
- **Botón dividido "Pista ▾"**: se elige Pista o Conectar con la flechita.
- Tres vistas: componentes (arriba), cobre visto de abajo (espejado), hoja para planchar (negro, **sin espejar** porque el cobre va abajo).
- **Lado componentes**: cada pieza muestra en el centro su nomenclador (R1, IC1…) y abajo su valor, como la serigrafía (`drawCompLabel`, pedido de Matías). Con borde del color del fondo para leerse sobre las patas; en piezas angostas y altas va de costado. En la vista de cobre queda solo el nomenclador arriba a la izquierda.
- Cuadros de opciones con el estilo del autorruteador: bloques con título, interruptores para sí/no, botones unidos para pocas opciones, listas para muchas.

## Qué hace hoy (todo en `index.html`)

**Biblioteca y mesa**
- **Ejemplo precargado** (si no hay diseño guardado): detector de movimiento con LDR (`exampleLdr`, datos en `EX_LDR`: esquema de Thiago, E.E.S.T. N.º 2; dos LDR en puente, LM741, NE555, LED y buzzer, bornera de alimentación). Placa de **5 × 5 cm ya ruteada** (pedido de Matías): masa toda con pistas (una va por el borde), relleno sin conectar, 2 puentes de masa y "THIAGO RUSSO" en cobre; presets de carbón de 10 mm. Se armó a mano (ubicación pensada por Claude + autorruteador + búsqueda de variantes); las posiciones van sin enganche (`snapComp` no se aplica). Archivo → Ejemplos también abre el **temporizador con NE555** (`exampleTimer`, `EX_TIMER`; actividad extra de Thiago: VR1 1 MΩ + R2 a las patas 6 y 7 con C1 220 µF, R1 + C2 a la pata 2, LED con R3 470 Ω en paralelo con el buzzer en la salida; pulsador S1 afuera, en el cable de la batería; 5 × 5 cm ruteado sin puentes, masa con pistas, relleno sin conectar y "THIAGO RUSSO 4° 3" en cobre) y el del 555 con un LED (`example`). Los ejemplos se cargan con `loadExample(EX)`.
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
- Marca en rojo: corto, separación < 0,6 mm, pista < 0,5 mm, cobre a menos de 2 mm del borde o en la zona de un agujero, esquinas fuera de la regla de 45°, conexiones sin rutear. Ángulo agudo: en cada pata o unión se miran las direcciones de las pistas que salen; si dos forman menos de 90° se marca (una unión en T a mitad de otra pista vale y también cuenta como conexión; un puente cuenta como unido a la pista que pasa por su punta).
- **Clic derecho sobre la marca**: explica en palabras simples (`DRC_WHY`) y ofrece arreglarlo (`drcFixes`): ancho a 0,8 mm, rehacer con 45°, rutear por otro lado, correr un componente (`moveCompFix`), agrandar el contorno, quitar agujeros, rutear lo que falta. Nunca toca lo que tiene candado.

**Autorruteador** (tecla A, `autoroute`; cuadro `routeDlg`; opciones en `prefs.route`)
- Grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo giros de 45°. Cerca de cada pata (hasta 0,9 mm del pad) no deja salir ni llegar una pista a menos de 90° de otra que ya sale de esa pata (`padOf`, `acute` en `routeOne`). Las pistas salen y llegan a un pad (sin uniones en T). **Esquiva también las pistas de su misma red** (nada de pistas pegadas o encimadas), salvo a 0,9 mm de la pata de salida o llegada (`nearP` en `routeOne`). Varias pasadas de arrancar y rerutear (Rápido/Normal/A fondo = 4/12/30).
- Bloques del cuadro: **Pistas** (ancho de señal y de alimentación/masa, **los dos 0,8 mm por defecto**: pedido de Matías, todas las pistas iguales; `anchos08` pisa una vez lo guardado; solo se ensancha si la conexión tiene corriente indicada, separación 0,8 cómoda o 0,6, primero alimentación y masa), **Puentes de alambre** (opcional; máximo 1/2/3/5; largo 7,62/10,16; nunca debajo de un componente; `doc.jumpers`), **Placa** (reacomodar componentes, tamaño: no tocar / mínimo / estándar 5×5 a 15×20 cm, agujeros de fijación), **Terminación** (lágrimas, plano de masa, conservar pistas dibujadas o solo las fijas, esfuerzo).
- Detecta alimentación y masa por nombre de pata (GND/VCC/VDD/VSS/V+/V−) y por la entrada/salida de reguladores.
- **Reacomodar** (`placeComps`): recocido simulado en grilla de 2,54 mm; respeta candados; cuida largo de conexiones, cruces, superposición (aire de 0,6 mm), desacople junto al integrado, reguladores y borneras al borde. La masa cuenta para largo y cruces como cualquier red. Movimientos: correr, girar, intercambiar y "hacia lo que conecta".
- **Ubicación por bloques** (`placeBlocks`, `o.smart`): cada pieza con el integrado con el que más se conecta (sin contar alimentación y masa), bloques en el orden de la señal, cada integrado prueba los 4 giros con sus piezas alrededor; después un recocido suave.
- **Probar variantes y elegir** (`routeVariants`, interruptor en el bloque Placa cuando se reacomoda; también lo usa el asistente): varias ubicaciones por bloques con distinta semilla y después cambios chicos sobre la mejor (mover, girar, intercambiar), cada una ruteada de verdad y puntuada (sin rutear ×1000, puentes ×120, errores ×400, largo). Dura 20 s / 1 min / 3 min según el esfuerzo, se puede parar, y al final muestra las 3 mejores con imagen para elegir. Todo es un solo paso de deshacer.
- **Patas intercambiables** (`swapEquivalentPins`): los extremos de presets y potenciómetros se dan vuelta si así quedan menos cruces (solo cambia el sentido de giro). Nunca da vuelta uno que tenga pistas conservadas en sus patas: quedaría un corto.

**Cobre extra**
- **Texto en cobre** (herramienta Texto, tecla X; `doc.texts`, `textPolys`, `textDlg`, `textCtx`): letra de un trazo Hershey Sans (`HFONT`, MIT). Cada letra son tramos de pista: sale en plancha, PDF y Gerber, entra en la revisión de reglas, el plano la rodea, el autorruteador y el reacomodador la esquivan. Se guarda espejado para leerse derecho del lado del cobre. Se arrastra, se edita y se borra; alto 2 a 5 mm, trazo 0,5/0,6/0,8 mm. Signos extra que no trae la letra Hershey: `HEXTRA` (hoy el °).
- **La masa siempre va con pistas** (pedido de Matías, 27/11/2026): el autorruteador rutea todas las redes, masa incluida, haya plano o no. Así la placa anda igual sin plano. (`opt.skip`, `opt.withPlane` y `planeTargets` quedan en el código pero `routeCore` ya no los usa.)
- **Lágrimas** en los pads (`tearShapes`), solo si respetan 0,6 mm.
- **Plano de masa** (`planeGeo` decide qué queda; `drawPlane` lo dibuja liso). Atado al contorno, hasta 2 mm del borde. **Rellena también los espacios vacíos** como cobre suelto para ahorrar percloruro (`doc.plane.fill`). **Alivio térmico** en las patas de masa: 0,6 mm libres y 4 rayos de 0,8 mm, solo los que llegan al plano (`doc.plane.thermal`). Sigue a las pistas en vivo mientras se arrastra. Sin GND, igual rellena (`doc.plane.key=null`). **Relleno sin conectar** (`doc.plane.iso`, pedido de Matías): el plano rellena igual pero no toca ninguna pista ni pad (todo con 0,8 mm de aire, sin alivios); la masa va con pistas. **Es lo que se pone por defecto** (plano nuevo, ejemplos y autorruteador). Se cambia en Herramientas, en el clic derecho del tablero y en el autorruteador (Plano: Sin conectar / Unido a masa, `o.planeIso`).
- **Agujeros de fijación** opcionales: 3 mm por defecto, en las esquinas a 4 mm del borde, sin cobre hasta 2 mm alrededor. Los de esquina siguen al contorno; se arrastran y se les cambia el diámetro con clic derecho (`doc.holes`).

**Imprimir y exportar** (menú Archivo)
- **Imprimir hoja para planchar** (Ctrl+P, `printSheet`): tamaño real en A4, ~600 ppp, con una **barra de 5 cm** para comprobar la escala (imprimir al 100 %).
- **Imprimir varias por hoja…** (`multiDlg`): copias 2/4/6/8 o todas las que entren, separación 2/5/10 mm; elige solo A4 parada o acostada y placa derecha o girada (`sheetLayout`). Imprime o exporta PDF.
- **Exportar PDF 1:1** (`exportPdf`, `buildPdf`: PDF armado a mano, sin librerías).
- **Exportar Gerber** (`exportGerber`): ZIP con cobre `.gbl` (plano y alivios incluidos), contorno `.gko` y agujeros `.drl`.
- **Exportar diseño** a `.json` (descargar o copiar) e importarlo.

**Cuentas con Google** (Firebase, `firebase-config.js`)
- Botón **Entrar con Google** arriba a la derecha; con sesión muestra foto o inicial, nombre y menú (Mis proyectos, Guardar, Salir).
- **Sin cuenta se puede todo**: guardar y abrir van al navegador; imprimir y exportar, directo. Con cuenta, guardar y abrir van a la nube (`usingCloud()` = servicio listo y sesión iniciada).
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
| `firestore.rules` | Reglas de seguridad de Firestore. `users/{uid}` (créditos) solo se lee; lo cambia el servidor. Se publican con `firebase deploy --only firestore:rules`. |
| `functions/` | **Sin uso hoy.** Servidor del asistente con IA que se sacó de la página (Firebase Functions): `index.js` (cuenta, créditos, llamada a Claude), `nucleo.js` (instrucciones, formato de respuesta, validación, links; se prueba con `node prueba.js`), `catalogo.txt` (generado). |
| `firebase.json`, `.firebaserc` | Configuración para subir el servidor y las reglas. |
| `docs/configurar_asistente.md` | Sin uso hoy. Cómo se activaba el asistente (Blaze, clave de Anthropic, subir el servidor) y cuánto cuesta. |
| `docs/configurar_firebase.md` | Cómo se configuró Firebase, paso a paso. |
| `docs/investigacion_ruteo.md` | Investigación de reglas y algoritmos de ruteo, con fuentes. |
| `guia.html`, `privacidad.html`, `terminos.html` | Guía para hacer la plaqueta, política de privacidad y términos de uso (dicen que es gratis, sin publicidad ni pagos). Enlazadas desde el menú Ayuda. |
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
