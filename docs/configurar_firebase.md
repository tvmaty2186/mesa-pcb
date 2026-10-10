# Configurar las cuentas con Google (Firebase)

Mientras esto no esté hecho, Mesa PCB funciona como siempre: los diseños se guardan en el navegador de cada uno.
Cuando esté listo, cada usuario entra con su cuenta de Google y guarda sus proyectos en la nube.
Sin cuenta solo se puede dibujar y diseñar: guardar, abrir, imprimir y exportar piden entrar.

Es gratis (plan Spark de Firebase). Lleva unos 10 minutos.

## 1. Crear el proyecto
1. Entrá a https://console.firebase.google.com con tu cuenta de Google.
2. **Crear un proyecto** → nombre: `mesa-pcb` → Google Analytics: **no hace falta** → Crear.

## 2. Prender el inicio de sesión con Google
1. En el menú de la izquierda: **Compilación → Authentication → Comenzar**.
2. Pestaña **Método de acceso** → **Google** → **Habilitar** → elegí tu correo como correo de asistencia → **Guardar**.
3. Pestaña **Configuración → Dominios autorizados → Agregar dominio** → `tvmaty2186.github.io` → Agregar.

## 3. Crear la base de datos
1. **Compilación → Firestore Database → Crear base de datos**.
2. Ubicación: `southamerica-east1 (São Paulo)` → **Iniciar en modo de producción** → Crear.
3. Pestaña **Reglas**: borrá lo que hay, pegá el contenido del archivo `firestore.rules` de este repositorio y tocá **Publicar**.
   Esas reglas hacen que cada usuario vea y toque solo sus propios proyectos.

## 4. Registrar la página web y pasar los datos
1. Arriba a la izquierda, el engranaje → **Configuración del proyecto**.
2. Abajo, en **Tus apps**, tocá el ícono **</>** (Web) → apodo: `Mesa PCB` → **Registrar app** (sin Hosting).
3. Aparece un bloque `const firebaseConfig = { apiKey: "...", authDomain: "...", ... }`.
   **Copiá ese bloque y pasáselo a Claude** (o pegalo vos en `firebase-config.js`, en lugar de `null`).
   Esos datos no son secretos: identifican tu proyecto; la seguridad la dan las reglas del paso 3.

## Cómo queda `firebase-config.js`
```js
window.FIREBASE_CONFIG = {
  apiKey: "AIza…",
  authDomain: "mesa-pcb-xxxx.firebaseapp.com",
  projectId: "mesa-pcb-xxxx",
  storageBucket: "mesa-pcb-xxxx.appspot.com",
  messagingSenderId: "…",
  appId: "…"
};
```

## Para más adelante
- Para ver cuántos usuarios hay: Authentication → Usuarios.
- Si algún día la página va en un dominio propio, agregalo en "Dominios autorizados".
- El plan gratis alcanza de sobra para empezar (50 000 lecturas y 20 000 escrituras por día).
