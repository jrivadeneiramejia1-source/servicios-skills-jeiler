# Estado de la línea de servicios (2026-11-05)

Prioridad de Jeiler: **1) agentes y WhatsApp**, luego Excel, apps y video. Cuentas gratis: Cloudflare y Google. Solo herramientas gratis **sin tarjeta**. Tiene 3 clientas conocidas para un **piloto gratis** (flores de foami, fresas con crema, gorras); usan WhatsApp y quiere comparar WhatsApp con Telegram.

## Hecho
| Qué | Dónde | Estado |
|---|---|---|
| Bot de pedidos (Telegram y WhatsApp) | repo `plantilla-bot-negocio` (ya en `main`) | Probado con simulación y Worker local; **no** con cuentas reales |
| Kit comercial: briefing, cotizador, alcance y entrega, oferta y portafolio, privacidad | este repo | Plantillas y cotizador probado con datos inventados; **nada con un cliente real ni revisado por un abogado** |

## Hallazgos que cambian cómo se vende (búsqueda del 2026-11-05)
Marcados según el informe de la búsqueda: **V** = leído en una página oficial ese día; **NV** = solo resúmenes.
- **V** WhatsApp oficial: desde el 1 de octubre de 2026 solo hay 1.000 mensajes de servicio gratis al mes por número; sin método de pago registrado en Meta, pasado el tope los mensajes no se entregan. **NV:** tarifa en Colombia y qué tarjetas acepta Meta.
- **V** Telegram: los bots escriben sin costo (la API es gratis).
- **V** Cloudflare gratis: D1 con 100.000 filas escritas por día; Workers con 100.000 solicitudes y 10 ms de CPU por día. Con el bot de `plantilla-bot-negocio`, cada mensaje escribe unas 2 a 4 filas, así que el tope diario queda lejos para un negocio chico (**cuenta aproximada, no medida**). Si se pasa, el bot deja de responder hasta el día siguiente.
- **V** n8n: no hay dónde correrlo 24/7 gratis y sin tarjeta que sirva (Render se duerme a los 15 minutos; Koyeb pide tarjeta). Por eso el bot va en Cloudflare, no en n8n.
- **V** Google Play cuesta 25 USD con tarjeta: no es gratis. PWA primero, APK por enlace si el cliente insiste.
- **V** Google Apps Script (cuenta gmail.com): 6 minutos por ejecución y 100 correos al día.
- **NV** Límites de Gemini, Groq, OpenRouter y Mistral gratis; y que Gemini y Mistral gratis pueden usar los datos para entrenar (por eso no se les mandan datos de clientes).
- No hay plantillas contables colombianas con licencia clara: habría que hacerlas propias.

## Lo que sigue (cada paso con el «sí» de Jeiler)
1. Subir este kit (rama y PR).
2. **Copia de pedidos a Google Sheets** en `plantilla-bot-negocio` (Apps Script desde la cuenta del cliente, sin archivo de claves).
3. **Excel contable:** skill propia con plantillas inventadas y reglas para datos reales (permiso escrito, trabajar en copia, no subir a servicios externos). Se apoya en la skill `xlsx` de la cuenta.
4. Piloto con las tres clientas: aviso de privacidad, alcance y acta; medir WhatsApp contra Telegram con `/resumen`.
5. Revisión por un contador (cotizador, factura, impuestos) y un abogado (aviso, política, datos).

## Qué falta decidir (de Jeiler)
- Cuánto quiere ganar al mes, para calibrar la tarifa por hora (por ahora no lo sabe).
- Cuál de las tres clientas empieza primero, y si el piloto va con WhatsApp oficial (cuenta de Meta a nombre de la clienta) o solo Telegram.
