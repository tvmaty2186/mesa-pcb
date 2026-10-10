# Cómo activar el asistente con IA

El código ya está listo: la ventana del chat en `index.html` y el servidor en `functions/`. Para que ande hay que hacer esto **una sola vez**. Todo se hace desde el navegador; no hace falta instalar nada en la computadora.

## 1. Pasar Firebase al plan Blaze

Firebase solo deja usar un servidor con el plan Blaze. Es pago por uso: con poco uso cuesta casi nada, pero pide una tarjeta.

1. Entrá a console.firebase.google.com → proyecto **mesa-pcb**.
2. Abajo a la izquierda, **Actualizar** → **Blaze** → cargá la tarjeta.
3. Poné una **alerta de presupuesto**, por ejemplo de USD 10. Te avisa por correo si se pasa.

## 2. Sacar la clave de la API de Anthropic

1. Entrá a console.anthropic.com y creá la cuenta.
2. **Billing**: cargá saldo, por ejemplo USD 10. Es prepago, así que nunca gasta más de lo cargado.
3. **Limits**: poné un límite de gasto mensual.
4. **API Keys** → **Create Key** → copiala.

**No la pegues en el chat de Claude ni en ningún archivo.** Va directo al servidor en el paso 3.

## 3. Subir el servidor (desde Google Cloud Shell)

1. Abrí https://shell.cloud.google.com/?project=mesa-pcb con la misma cuenta de Google de Firebase. Se abre una terminal en el navegador.
2. Copiá y pegá estas líneas, de a una:

```
git clone https://github.com/tvmaty2186/mesa-pcb.git
cd mesa-pcb/functions && npm install && cd ..
npx -y firebase-tools@15 login --no-localhost
```

   El último comando te da un link. Abrilo, aceptá y pegá el código que te muestra.

3. Guardá la clave de Anthropic como secreto. Te la pide y no se ve mientras la pegás:

```
npx -y firebase-tools@15 functions:secrets:set ANTHROPIC_API_KEY
```

4. Subí el servidor y las reglas de Firestore:

```
npx -y firebase-tools@15 deploy --only functions,firestore:rules
```

Tarda unos minutos. Cuando termina, el asistente ya anda en la página.

## Para actualizar más adelante

Si cambia algo en `functions/` (o en la biblioteca, que genera `functions/catalogo.txt`), hay que volver a subirlo desde Cloud Shell:

```
cd mesa-pcb && git pull && npx -y firebase-tools@15 deploy --only functions
```

## Ajustes (en `functions/nucleo.js`, arriba de todo)

| Ajuste | Qué es | Hoy |
|---|---|---|
| `MODELO` | Qué modelo de Claude se usa | `claude-opus-5-5` (el más capaz; USD 4 por millón de tokens de entrada y USD 20 de salida) |
| `GRATIS_POR_MES` | Consultas gratis por usuario por mes | 5 |
| `LIM` | Límites de tamaño (texto, archivos, páginas de PDF) | ver el archivo |

**Cuánto cuesta cada consulta (aproximado, con Opus 5.5):**

- Una pregunta común: entre USD 0,01 y 0,05.
- Una foto o un esquemático: entre USD 0,05 y 0,15, según lo grande que sea el circuito.

Son estimaciones: el costo real se ve en `users/{uid}/consumo` después de las primeras pruebas.

La biblioteca y las instrucciones fijas se guardan en caché unos minutos, así que las consultas seguidas salen más baratas.

**Cuántos créditos descuenta cada consulta:**

- 1 por mensaje.
- +1 si lleva imágenes.
- +1 por cada 10 páginas de PDF.
- +1 si lleva un link.

## Cómo controlar el gasto

- Cada consulta queda anotada en Firestore, en `users/{uid}/consumo`, con los tokens usados.
- El gasto total se ve en console.anthropic.com → **Usage**.
