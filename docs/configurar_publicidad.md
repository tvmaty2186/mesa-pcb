# Cómo conectar la publicidad (AdSense + Ad Manager)

El código ya está listo. Solo falta completar **`publicidad.js`** con tres datos. Mientras estén en `null`, la página muestra los espacios reservados.

| Dato en `publicidad.js` | Qué es | De dónde sale |
|---|---|---|
| `adsenseClient` | Código de editor, `ca-pub-…` | AdSense → Cuenta → Información de la cuenta |
| `bannerSlot` | Número del bloque del banner de abajo | AdSense → Anuncios → Por bloque de anuncios → Anuncio gráfico |
| `rewardedUnit` | Ruta del bloque con recompensa, `/RED/nombre` | Ad Manager → Inventario → Bloques de anuncios |

## Orden de los pasos

1. **Dominio propio** (AdSense no aprueba `github.io`).
   - En el registrador del dominio: 4 registros `A` a `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` y un `CNAME` de `www` a `tvmaty2186.github.io`.
   - En GitHub → repositorio → Settings → Pages → Custom domain: escribir el dominio y tildar **Enforce HTTPS** (crea el archivo `CNAME`).
   - En Firebase → Authentication → Settings → **Dominios autorizados**: agregar el dominio (si no, no anda "Entrar con Google").
2. **AdSense**: adsense.google.com → agregar el sitio con el dominio. Google da el código `ca-pub-…`; ponerlo en `adsenseClient`. La revisión tarda de días a semanas.
3. **`ads.txt`** en la raíz del repositorio, con esta línea (cambiando el número):
   `google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0`
4. **Mensaje de privacidad** (consentimiento): AdSense → Privacidad y mensajes → crear el mensaje para Europa y Reino Unido. Google lo exige; se activa desde ahí, sin tocar código.
5. Con AdSense **aprobado**: crear el bloque del banner (`bannerSlot`).
6. **Ad Manager**: admanager.google.com → crear la cuenta con la misma cuenta de Google de AdSense. Después: Inventario → Bloques de anuncios → Nuevo → tamaño "Fuera de página" → formato **Con recompensa (web)**. La ruta queda como `/NÚMERO_DE_RED/mesa_pcb_recompensa`; ponerla en `rewardedUnit`. En Ad Manager hay que activar que AdSense llene ese bloque (Administrador → Configuración global → AdSense / "Maximizar el rendimiento").

## Cómo funciona en la página

- Banner: se carga AdSense dentro de `#ad-slot` (`adsInit`).
- Antes de guardar, imprimir, exportar, importar o autorrutear (`withAd`): se pide un aviso con recompensa. Si hay, el botón dice **"Ver aviso y seguir"**; al terminarlo sigue la acción. Si lo cierra antes, la acción se cancela.
- Si Google no tiene aviso para dar (o un bloqueador lo frena), aparece el espacio reservado con la cuenta regresiva de 5 s. La acción nunca queda trabada.

## Límites a saber

- Los anuncios con recompensa en web llenan poco al principio; muchas veces se va a ver la cuenta regresiva.
- Con pocas visitas Ad Manager paga poco; lo importante es que AdSense apruebe el sitio.
