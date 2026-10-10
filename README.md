# Mesa PCB

Programa web gratis para diseñar plaquetas de **una cara**, con componentes de **agujero pasante**, pensado para hacerlas en casa con **planchado y percloruro**. Sin librerías para descargar: la biblioteca de componentes ya viene incluida.

**Usalo acá:** https://tvmaty2186.github.io/mesa-pcb/

## Qué hace

- Biblioteca de 161 componentes listos para arrastrar al tablero.
- Conexiones, pistas a mano con quiebres de 45° y **autorruteador** (con puentes, reacomodo de componentes y tamaño de placa).
- **Revisión de reglas**: marca los errores en rojo, los explica y los arregla solo.
- **Plano de masa** con alivio térmico y relleno para gastar menos percloruro, lágrimas y agujeros de fijación.
- Agrupar, mover y rotar partes de la placa (o la placa entera).
- **Imprimir la hoja para planchar** a tamaño real, una o varias por hoja, PDF 1:1 y **Gerber** para fabricar.
- **Cuenta de Google**: cada usuario guarda sus proyectos en la nube. Sin cuenta se puede dibujar y diseñar, pero no guardar, imprimir ni exportar.

## Archivos

- `index.html`: la mesa de trabajo.
- `huellas.html`: buscador de huellas por nombre de componente.
- `biblioteca/`: los componentes y el programa que los genera.
- `firebase-config.js` y `firestore.rules`: cuentas y proyectos en la nube.
- `docs/`: investigación de reglas y ruteo, y cómo se configuró Firebase.
- `CLAUDE.md`: contexto completo y decisiones del proyecto.
