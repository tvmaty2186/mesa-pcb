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
- **Panel izquierdo solo con la biblioteca** (por categorías, tipo acordeón) y una vista previa abajo. Ancho ajustable arrastrando el borde. Sin sección de herramientas en el panel.
- Se arrastra al tablero **desde la lista o desde la vista previa**, con fantasma enganchado a la grilla.
- **Barra de propiedades fina (32 px) arriba, dentro de la mesa**, al seleccionar algo. Nunca un panel lateral. Botones con ícono. El dibujo no se mueve cuando aparece.
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
- Conexiones editables y pista manual con quiebres de 45° automáticos y selector de ancho.
- Revisión de reglas (DRC): Herramientas → Revisar reglas, tecla D o botón Reglas. Marca en rojo separación < 0,6 mm entre redes distintas, pista < 0,5 mm, cobre a menos de 2 mm del borde, esquinas y uniones de pistas fuera de la regla de 45°, y conexiones sin rutear. La lista lleva a cada problema. Código en `runDrc` (`index.html`); las marcas se apagan en Ver.

- Autorruteador v1 (parte 1): Herramientas → Autorruteador, tecla A o botón de la barra. Grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo giros de 45°, separación y borde según las reglas. Opciones: ancho de señal, ancho de alimentación y masa (detecta GND/VCC/VDD/VSS/V+/V− por nombre de pata y la entrada/salida de reguladores), rutear primero alimentación y masa, conservar o borrar las pistas ya dibujadas. Hasta 12 pasadas de arrancar y rerutear (las que fallan van primero, después cambia el orden con azar repetible). Las pistas siempre salen y llegan a un pad (sin uniones en T). Código en `autoroute` (`index.html`).

Próximos pasos, en este orden:
1. **Autorruteador v1, parte 2**: puentes (sí/no, máximo, largos 7,62 / 10,16 mm), plano de masa al final y candado para fijar componentes y pistas.
2. Imprimir / exportar PDF a escala 1:1 para planchar.
3. Asistente con IA.

### Opciones del autorruteador
- **v1:** incluir puentes (sí/no, máximo, largos 7,62 / 10,16 mm); optimizar recorrido; fijar componentes y pistas con candado; anchos de señal y potencia (o por corriente); rutear primero alimentación y masa; plano de masa al final (sí/no). Algoritmo: grilla de 0,635 mm, A* con costos (largo, quiebres, cercanía), solo direcciones a 45°, varias pasadas de arrancar y rerutear.
- **v2:** reacomodar componentes (respetando los fijados, desacople junto al integrado, reguladores al borde, entrada de audio lejos de la salida); optimizar tamaño a una placa estándar elegida.
- **Descartado por ahora:** informe final.

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
