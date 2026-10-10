# Mesa PCB: contexto para Claude

Este archivo es para que cualquier sesión de Claude retome el proyecto sin empezar de cero. Leelo completo antes de tocar código.

## Quién y qué

- Dueño: Matías. Técnico electrónico con casi 20 años en mantenimiento y electromecánica.
- Producto: **Mesa PCB**, un programa web para diseñar plaquetas de circuito impreso, gratis y con publicidad (banner).
- Público: **adultos** (mayores de 18). Aficionados y técnicos que hacen placas en casa.
- Gran diferencia con KiCad o EasyEDA: **cero librerías para descargar**. Las huellas se calculan desde encapsulados estándar y vienen en una biblioteca propia.
- A futuro: asistente con IA (dictar "agregá un 555 y conectá la pata 3 al LED"), modo esquema y 3D.

## Cómo hablar con Matías

- Castellano rioplatense (voseo). Respuestas **cortas, claras y en orden**. Frases simples.
- Prefiere dictar y escuchar: evitá bloques largos de texto y tecnicismos sin explicar.
- Al terminar un cambio: decí qué cambió en pocas líneas, sin repetir todo lo hecho.
- Si algo no se puede o tiene un límite, decilo de entrada y con honestidad.

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

Detalle y fuentes en `docs/investigacion_ruteo.md`.

## Decisiones de interfaz (pedidas por Matías)

- Tablero casi a pantalla completa. Líneas de 1 cm, grilla fina, reglas y enganche: **cada una se prende y apaga**.
- Menús clásicos arriba (Archivo, Editar, Ver, Herramientas, Preferencias, Ayuda) y barra de herramientas con deshacer/rehacer.
- **Barra de herramientas solo con íconos**: el nombre aparece al pasar el mouse (atributo `title`), nunca como texto visible.
- **A la derecha de la barra**: un ícono por vista (lado componentes, lado cobre, hoja para planchar). La función "tamaño real 1:1" en pantalla se probó y **se sacó a pedido de Matías** (complicada, no suma): no volver a agregarla. La escala real va en la impresión.
- **Panel izquierdo solo con la biblioteca** (por categorías, tipo acordeón) y una vista previa abajo. Ancho ajustable arrastrando el borde. Sin sección de herramientas en el panel.
- Se arrastra al tablero **desde la lista o desde la vista previa**, con fantasma enganchado a la grilla.
- **Barra de propiedades fina (32 px) arriba, dentro de la mesa**, al seleccionar algo. Nunca un panel lateral. Botones con ícono. El dibujo no se mueve cuando aparece.
- **Clic derecho** abre un menú con las acciones de lo que está debajo: componente (rotar, candado, desconectar, duplicar, borrar), pista (ancho, candado, borrar), conexión (corriente, invertir, borrar), contorno (ajustar al mínimo, agujeros, plano, borrar) y tablero vacío (autorruteador, reglas, plano, alivio térmico, lágrimas, agujeros). Si el clic cae justo sobre el cobre de una pista, gana la pista aunque esté debajo de un componente. Código en `showCtx` y el listener `contextmenu`.
- **Sin textos de ayuda automáticos** (nada de carteles que expliquen cómo usar una herramienta). Solo avisos cortos de confirmación.
- **Sin barra de estado** abajo (se sacó para ganar espacio).
- **Franja publicitaria reservada abajo de todo**: 468 × 60 en computadora, 320 × 50 en celular. Ver comentario en `index.html` donde va el código del aviso.
- **Botón dividido "Pista ▾"**: se elige Pista o Conectar con la flechita.
- **Conectar**: une pad con pad con una línea punteada (lista de conexiones). Las líneas se seleccionan, se borran, se invierten y sus extremos se arrastran a otro pad.
- **Contorno de placa**: se dibuja al final, como herramienta de forma (clic en una esquina y arrastrar).
- Tres vistas: componentes (arriba), cobre visto de abajo (espejado), hoja para planchar (negro, **sin espejar** porque el cobre va abajo).

## Estado actual

Hecho:
- Biblioteca de 161 componentes y 97 encapsulados (resistencias, capacitores, diodos, LEDs, transistores TO-92/TO-126/TO-220, reguladores, integrados DIP, microcontroladores, amplificadores de audio Pentawatt/Multiwatt, relé, jack, borneras…).
- Mesa de trabajo: colocar, mover, rotar (R), duplicar, borrar, selección múltiple, deshacer/rehacer, contorno, medir, guardar/abrir en el navegador, exportar/importar JSON, tema claro/oscuro.
- Conexiones editables y pista manual con quiebres de 45° automáticos y selector de ancho. **Una pista que une pads vale como Conectar** (`linksFromTracks`): al terminarla se agregan las conexiones que falten, y el autorruteador hace lo mismo antes de rutear (sirve para diseños hechos solo con pistas). Así se puede autorrutear y, si se borra la pista, queda la línea punteada. Si la pista une dos conexiones distintas no se mezclan: avisa "corto" y la revisión de reglas lo marca (error **Corto**, con arreglo: sacar esas pistas y rutear bien).
- Revisión de reglas (DRC): Herramientas → Revisar reglas, tecla D o botón Reglas. Marca en rojo separación < 0,6 mm entre redes distintas, pista < 0,5 mm, cobre a menos de 2 mm del borde, esquinas y uniones de pistas fuera de la regla de 45°, y conexiones sin rutear. La lista lleva a cada problema. Código en `runDrc` (`index.html`); las marcas se apagan en Ver. **Clic derecho sobre una marca roja** explica el error en palabras simples (`DRC_WHY`) y ofrece corregirlo solo (`drcFixes`): poner la pista en 0,8 mm, rehacer la pista con 45°, rutear de nuevo por otro lado, separar o correr un componente de a 2,54 mm (`moveCompFix`), agrandar el contorno, quitar los agujeros o rutear lo que falta. Nunca toca lo que tiene candado.

- Autorruteador v1: Herramientas → Autorruteador, tecla A o botón de la barra. Grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo giros de 45°, separación y borde según las reglas. Las pistas siempre salen y llegan a un pad (sin uniones en T). Código en `autoroute` (`index.html`). **Cuadro de opciones** (`routeDlg`, rediseñado a pedido de Matías): ancho, 4 bloques (Pistas, Puentes de alambre, Placa, Terminación) con interruptores para sí/no, botones unidos para pocas opciones y listas para anchos y placas; lo que depende de otra opción aparece solo cuando hace falta. Opciones (se recuerdan en `prefs.route`):
  - Ancho de señal y de alimentación/masa (detecta GND/VCC/VDD/VSS/V+/V− por nombre de pata y la entrada/salida de reguladores). Rutear primero alimentación y masa.
  - Separación cómoda: prefiere 0,8 mm y baja a 0,6 solo donde no entra.
  - Pistas dibujadas: conservarlas todas o solo las fijas (candado).
  - Puentes de alambre (opcional): máximo 1/2/3/5, largo 7,62, 10,16 o los dos. Recto, del lado de componentes, nunca debajo de un componente. Solo se usan si la conexión no entra sin puente. Se guardan en `doc.jumpers` (`{id,a:[x,y],b:[x,y]}`), pad de 2 mm.
  - Lágrimas en los pads (`doc.tears`), plano de masa al terminar (`doc.plane={key}`), esfuerzo Rápido/Normal/A fondo (4/12/30 pasadas de arrancar y rerutear).
- Candado: botón en la barra de propiedades para componentes (uno o varios) y pistas. Lo fijo no se mueve, no se rota ni se borra.
- **Selección múltiple y grupos**: el rectángulo de Seleccionar toma componentes, pistas y puentes que queden adentro (`sel`, `selT`, `selJ`; `sel.clear()` limpia las tres). Lo seleccionado se mueve, rota (alrededor de un punto de grilla), duplica, fija y borra todo junto. Clic derecho sobre la selección: Rotar todo, **Agrupar / Desagrupar** (Ctrl+G / Ctrl+Shift+G), candado, desconectar, duplicar, borrar. El grupo se guarda como `group` en cada componente, pista y puente; al tocar cualquier parte se selecciona el grupo entero. Las pistas que llegan al grupo desde afuera no se mueven: se rutean de nuevo. Ctrl+A selecciona todo, pistas incluidas. **El contorno también entra** (`selO`, pedido de Matías): si el rectángulo lo encierra entero queda seleccionado, y los agujeros movidos a mano también (`selH`; los de esquina siguen al contorno). Al agrupar, el contorno guarda `group`; tocar su borde selecciona y arrastra el grupo. Mover o rotar el grupo lleva contorno, agujeros y plano de masa juntos (al rotar, el contorno cambia ancho por alto).
- Lágrimas: se calculan al vuelo (`tearShapes`), solo si respetan 0,6 mm. También en Herramientas → Lágrimas en los pads.
- Plano de masa: cobre en lo que sobra, a 0,8 mm de todo, unido a GND, sin islas ni tiras finas de menos de 0,8 mm ni pedazos de menos de 4 mm² (pedido de Matías: nada de puntitos sueltos). Se **dibuja liso** (`drawPlane`: rectángulo de la placa menos el cobre ajeno agrandado, en un canvas aparte); la grilla (`planeGeo`, de 0,08 a 0,25 mm según el tamaño de la placa) solo decide qué partes tocan masa y qué islas o tiras se borran. Los dos usan el mismo margen para que no queden hilitos, y el dibujo liso se recorta a lo que la grilla deja (más un paso), así no aparecen puntitos sueltos en rincones. **Sigue a las pistas en vivo**: mientras se arrastra (componentes, pistas, grupos o agujeros) el plano y las lágrimas se ven y se recalculan con grilla gruesa (≥ 0,2 mm) hasta 8 veces por segundo; al soltar o rotar se recalcula fino. **Rellenar espacios vacíos** (`doc.plane.fill`, por defecto sí, pedido de Matías para ahorrar percloruro): las partes que no tocan masa también quedan como cobre suelto, a 0,8 mm de todo (sin corto); se borran los pedacitos de menos de 4 mm² y las tiras de menos de 0,8 mm. Sin masa (GND) en el diseño, el relleno igual se hace, todo suelto (`doc.plane.key=null`). Se apaga desde Herramientas o con clic derecho en el tablero. Une las patas de masa que toca. Va atado al contorno: lo llena hasta 2 mm del borde y se recalcula solo si el contorno cambia. También en Herramientas → Plano de masa. Con **alivio térmico** (por defecto sí, `doc.plane.thermal`): las patas de masa quedan rodeadas de 0,6 mm libres y unidas por 4 rayos de 0,8 mm, para que no disipen tanto y se suelden fácil. Solo se dibujan los rayos que llegan a una parte del plano que queda (nada de rayos colgando), y su largo sigue la forma de la pata.
- Reacomodar componentes (opción del autorruteador, `placeComps`): recocido simulado en grilla de 2,54 mm. Mueve, rota e intercambia lo que no tiene candado (ni lo unido a una pista fija). Costo: largo de conexiones, cruces de líneas de aire (cada cruce es un puente en una cara), superposición, salirse de la placa, capacitor de desacople cerca de la pata VCC del integrado, reguladores y borneras/jack al borde. Borra las pistas sin candado antes de reacomodar.
- Tamaño de la placa (opción del autorruteador): No tocar el contorno / Ajustar al mínimo (achica el contorno a lo que ocupa todo + 2 mm, `shrinkOutline`) / Placa estándar 5×5, 5×7, 7×9, 7,5×10, 10×10, 10×15, 15×20 cm (`STD_BOARDS`).
- **Agujeros de fijación (opcionales, se apagan)**: por defecto **3 mm** en las cuatro esquinas, a 4 mm de cada borde, sin cobre hasta 2 mm más allá del agujero. `doc.holes=[{id,corner,x,y,d}]`: los de esquina (`corner` 0-3) siguen al contorno; **se arrastran** con el mouse y desde ahí quedan donde los dejás (`corner:null`). **Clic derecho** en un agujero: diámetro (2,5 / 3 / 3,2 / 3,5 / 4 / 4,5 mm u otro), volver a la esquina, borrar. Clic derecho en el tablero: agregar un agujero ahí. El autorruteador, el reacomodo, el plano y la revisión de reglas los respetan.
- **No se suelta nada encima de otro**: ni un componente sobre otro componente o sobre la zona de un agujero, ni un agujero sobre un componente u otro agujero. Vale para arrastrar, colocar, soltar desde la biblioteca, rotar, flechas, duplicar (busca lugar libre) y la barra de propiedades. El fantasma se pinta en rojo donde no se puede. Si se suelta igual, vuelve a donde estaba (`compBlocked`, `holeBlocked`).
- **Ancho por corriente**: clic derecho en una conexión → Corriente 1/2/3 A (`link.amps`). El autorruteador usa 1 / 1,5 / 2 mm para esa red y nunca baja de ese ancho.
- **Imprimir y exportar** (menú Archivo):
  - **Imprimir hoja para planchar** (Ctrl+P, `printSheet`): dibuja la vista "plancha" en un lienzo aparte a ~600 ppp (`renderSheet`) y la imprime a tamaño real en A4 (apaisada si la placa es ancha), con título y una **barra de 5 cm** para comprobar que la impresora no cambió la escala (hay que imprimir al 100 %).
  - **Exportar PDF a escala 1:1** (`exportPdf`): PDF armado a mano (sin librerías): A4 o más grande si la placa no entra, la hoja como JPEG a escala exacta, título y barra de 5 cm.
  - **Exportar Gerber** (`exportGerber`): ZIP (`zipStore`, sin compresión) con cobre `.gbl` (RS-274X, mm; el plano se arma con polaridad oscura/clara igual que en pantalla, con alivios térmicos), contorno `.gko` y agujeros `.drl` (Excellon). Probado con un lector de Gerber aparte.
  - **Exportar diseño**: botón para descargar el `.json` además de copiar el texto.
- Contorno en **centímetros con decimales** (barra de propiedades y etiquetas). Internamente sigue en mm.

Próximos pasos, en este orden:
1. Pads más grandes donde sobre lugar, zonas prohibidas, varias alternativas para elegir.
2. Asistente con IA.

Pendiente de v2: "entrada de audio lejos de la salida" (falta saber qué pata es entrada/salida de audio en la biblioteca).

### Opciones del autorruteador
- **v1:** incluir puentes (sí/no, máximo, largos 7,62 / 10,16 mm); optimizar recorrido; fijar componentes y pistas con candado; anchos de señal y potencia (o por corriente); rutear primero alimentación y masa; plano de masa al final (sí/no). Algoritmo: grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo direcciones a 45°, varias pasadas de arrancar y rerutear.
- **v2:** reacomodar componentes (respetando los fijados, desacople junto al integrado, reguladores al borde, entrada de audio lejos de la salida); optimizar tamaño a una placa estándar elegida.
- **Descartado por ahora:** informe final.
- Pedidos de Matías (10/10/2026): opciones editables para puentes, optimizar tamaño, optimizar recorrido y reacomodar componentes. Sumadas: candado, ancho por corriente, separación cómoda, lágrimas, pads grandes, plano de masa, agujeros de fijación opcionales, zonas prohibidas, varias alternativas.

## Archivos

| Archivo | Qué es |
|---|---|
| `index.html` | La mesa de trabajo (todo en un solo archivo: HTML, CSS y JS). |
| `huellas.html` | Buscador de huellas: escribís los componentes en castellano y dibuja cada huella. |
| `biblioteca/build_lib.py` | **Fuente de verdad de la biblioteca.** Genera `componentes.json` y `componentes.js`. Verifica pines por huella y separación mínima. |
| `biblioteca/componentes.json` / `.js` | Biblioteca generada. **No editar a mano**: cambiar `build_lib.py` y correr `python3 build_lib.py` dentro de `biblioteca/`. |
| `docs/investigacion_ruteo.md` | Investigación de reglas y algoritmos de ruteo, con fuentes. |

`componentes.js` existe para que la página funcione abriéndola con doble clic (sin servidor). En GitHub Pages también sirve el `.json`.

## Notas técnicas

- Unidades internas: milímetros. Origen arriba a la izquierda, Y hacia abajo.
- Documento: `{name, comps:[{id,ref,name,enc,val,x,y,rot}], outline:{x,y,w,h}, tracks:[{id,pts:[[x,y]...],w}], links:[{id,a:"compId:pad",b:"compId:pad"}]}`.
- Rotación en pasos de 90° (`rot` 0 a 3). El pin 1 se engancha a la grilla.
- Las funciones `path45` y `chamfer` aplican la regla de 45°: no las saltees en código nuevo de pistas.
- Antes de agregar un componente nuevo: verificá medidas en la hoja de datos o en las huellas oficiales de KiCad (en GitHub). Si el orden de patas no está confirmado, no lo inventes: dejalo sin tabla de pines y avisá.
