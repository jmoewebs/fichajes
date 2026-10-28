// Redirige el dominio antiguo (*.pages.dev) al dominio propio, conservando ruta y query.
// El dominio nuevo sigue su camino normal (archivos estáticos y /api/*).
const DOMINIO = "https://rumoresyfichajes.com";

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname.endsWith("pages.dev")) {
    return Response.redirect(DOMINIO + url.pathname + url.search, 301);
  }
  return context.next();
}
