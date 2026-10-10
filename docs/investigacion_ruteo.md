# Investigación: reglas y ruteo automático (Mesa PCB)

Fecha: 9 de octubre de 2026. Enfoque: placas de una cara, componentes de agujero pasante, planchado + percloruro.

## 1. Reglas de diseño propuestas (valores por defecto, ajustables)

| Regla | Valor | Por qué |
|---|---|---|
| Ancho de pista de señal | 0,8 mm | Para principiantes se recomienda empezar en 0,5 mm; el percloruro come entre 10 y 20 % del ancho por los costados (undercut). 0,8 mm deja margen. |
| Ancho mínimo absoluto | 0,5 mm | Por debajo hace falta impresora de alta resolución, papel especial y mucha práctica. |
| Separación entre cobre | 0,6 mm (preferido 0,8 mm) | Coincide con la regla ya usada en la biblioteca. |
| Distancia al borde de la placa | 2 mm | La placa se corta a mano (sierra o cúter); deja margen para limar. |
| Ángulos | **Decisión de Matías: nunca esquinas a 90°.** Cada cambio de dirección se hace con quiebres de 45° (una esquina de 90° se reemplaza por dos de 45°). Prohibidos también los ángulos agudos. Rige para pistas manuales, autorruteador y uniones en T. | Los ángulos agudos forman "trampas de ácido": el percloruro queda estancado y come de más. Con cloruro férrico el riesgo es alto. Los quiebres a 45° además reparten mejor el ataque y la corriente. |
| Uniones en T y pad-pista | Transición suave (lágrima) opcional | Evita cortes por ataque lateral. |
| Islas de cobre sueltas | Eliminarlas | Se despegan y pueden puentear pistas. |

### Ancho según corriente (fórmula IPC-2221, capa externa)
I = 0,048 · ΔT^0,44 · A^0,725 (A en mil², ΔT en °C). Con cobre de 1 oz (35 µm) y 10 °C de calentamiento:

| Corriente | Mínimo IPC | Valor sugerido en casa (con margen por undercut) |
|---|---|---|
| 1 A | 0,30 mm | 1,0 mm |
| 2 A | 0,78 mm | 1,5 mm |
| 3 A | 1,37 mm | 2,0 mm |

El programa calcula el mínimo con la fórmula y suma margen. Nunca menos de 0,8 mm.

### Dato clave para una cara
Entre dos pads vecinos de un integrado DIP quedan 0,74 mm. Una pista de 0,8 mm con 0,6 mm de separación a cada lado necesita 2,0 mm. **Ninguna pista puede pasar entre patas de un DIP.** Entre las dos filas del DIP (filas a 7,62 mm) sí entran hasta 3 pistas.

### Plano de masa (relleno de cobre)
Dejar cobre en lo que no es pista, conectado a GND, reduce la cantidad de cobre a disolver: gasta menos percloruro y ataca más rápido. Separación del relleno: 0,8 mm.

## 2. Algoritmos de ruteo automático

- **Lee (laberinto):** se arma una grilla, se expande una "onda" desde el pad de origen hasta tocar el destino y se vuelve por el camino más corto. Siempre encuentra camino si existe, pero explora mucho.
- **A\*:** igual que Lee pero con una estimación de cuánto falta, así busca hacia el destino en vez de en todas direcciones. Encuentra el camino óptimo explorando mucho menos.
- **Costos:** cada paso cuesta según largo, cambios de dirección, cercanía a otras pistas o al borde. Así se prefieren caminos limpios.
- **Ruteo global y detallado:** primero un recorrido aproximado por zonas, después el trazado fino.
- **Arrancar y rerutear (rip-up and reroute):** se rutean las conexiones en orden; si una falla, se levantan las que molestan y se reintenta con otro orden. Es el método más usado.
- **Orden de las conexiones:** influye mucho en el resultado. Se pueden probar varios órdenes y quedarse con el mejor.
- Todos son métodos aproximados: el problema completo no tiene solución exacta rápida. Los profesionales rutean a mano lo crítico y dejan el resto al autorruteador.

## 3. Plan para Mesa PCB

1. **Conexiones (líneas de aire):** el autorruteador necesita saber qué pata va con cuál. Primero: herramienta para unir pad con pad (y más adelante, el esquema).
2. **Pista manual:** dibujar pistas enganchadas a la grilla; las esquinas se convierten solas en dos quiebres de 45°. Nunca 90°.
3. **Revisión de reglas (DRC):** controla ancho, separación, ángulos, borde y conexiones faltantes.
4. **Autorruteador:** grilla de 0,635 mm (2,54 / 4), A* con costos, primero alimentación y masa (más anchas), después las conexiones cortas, varias pasadas de arrancar y rerutear.
5. **Puentes:** en una cara las pistas no se pueden cruzar. Si no hay camino, el programa propone un puente de alambre del lado de los componentes, con largo múltiplo de 2,54 mm, y trata de usar la menor cantidad posible.
6. **Plano de masa** opcional al final.

## 4. Opciones del autorruteador (decididas con Matías)

**Primera versión:** incluir puentes (sí/no, máximo de puentes, largos estándar 7,62 / 10,16 mm), optimizar recorrido (pistas cortas, pocos quiebres), fijar componentes y pistas con candado, anchos de pista (señal / potencia, o por corriente con IPC-2221), rutear primero alimentación y masa, plano de masa al final (sí/no).

**Segunda versión:** reacomodar componentes (respetando los fijados y reglas de electrónica: capacitor de desacople junto al integrado, reguladores cerca del borde, entrada de audio lejos de la salida), optimizar tamaño (con tamaño de placa estándar elegido por el usuario).

**Para más adelante:** zonas prohibidas, agujeros de fijación automáticos, nivel de esfuerzo, varias alternativas para elegir. El informe final quedó descartado por ahora.

## Fuentes
- NextPCB, calculadora IPC-2221: https://www.nextpcb.com/blog/pcb-trace-width-calculator-ipc-2221-guide
- ALLPCB, grabado casero: https://www.allpcb.com/allelectrohub/diy-pcb-etching-achieving-finer-line-widths-in-your-home-lab
- Foro KiCad, pistas para planchado: https://forum.kicad.info/t/trace-widths-for-toner-transfer-etching/11364
- PCBSync, trampas de ácido: https://pcbsync.com/acid-traps-pcb/
- Wikipedia, Routing (EDA): https://en.wikipedia.org/wiki/Routing_(electronic_design_automation)
- Tiny Computers, matemática del ruteo: https://tinycomputers.io/posts/the-mathematics-of-pcb-trace-routing.html
