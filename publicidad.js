// Configuración de la publicidad. Estos datos no son secretos: identifican la cuenta y los espacios.
// Mientras estén en null, la página muestra los espacios reservados (sin avisos reales).
// Cómo conseguir cada dato: docs/configurar_publicidad.md
window.ADS_CONFIG = {
  // AdSense: el código de editor, por ejemplo "ca-pub-1234567890123456".
  adsenseClient: null,
  // AdSense: el número del bloque de anuncios del banner de abajo, por ejemplo "1234567890".
  bannerSlot: null,
  // Ad Manager: la ruta del bloque de anuncios con recompensa, por ejemplo "/1234567/mesa_pcb_recompensa".
  rewardedUnit: null
};
