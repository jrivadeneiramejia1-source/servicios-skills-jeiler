---
name: briefing-cliente
description: >-
  Ayuda a entender qué necesita de verdad un cliente antes de cotizar o construir: 12 preguntas base y preguntas extra según el servicio (bot de WhatsApp o Telegram, apoyo con Excel, app web o APK, video). Detecta lo que falta, lo poco realista y lo que el cliente no sabe que podría pedir, y deja una hoja de briefing lista para guardar. Usar cuando Jeiler diga "me pidieron un bot", "una clienta quiere", "qué le pregunto a este cliente", "briefing" o antes de cotizar cualquier servicio.
---

# Briefing de cliente

Una conversación corta y ordenada antes de tocar nada. Evita construir lo equivocado y cobrar de menos.

## Reglas
- Un solo mensaje con todas las preguntas que falten, con opciones y una respuesta recomendada. Lo que el cliente no sepa responder se anota como «pendiente», no se inventa.
- **Datos de clientes y de sus compradores** (contabilidad, teléfonos, correos): no se pegan en chats con IA, ni en repos, ni en servicios externos sin permiso de su dueño. Para practicar, usar datos inventados.
- Guardar el briefing fuera del repo (es público). Este repo solo tiene la plantilla vacía y ejemplos inventados.
- Proponer lo que el cliente quizá no conoce (ver «Ideas»), sin vender de más.

## Proceso
1. Abrir `plantilla/briefing.md` y llenar la parte común (12 preguntas) con lo que el cliente ya dijo.
2. Hacer en un mensaje las preguntas que faltan. Añadir las del servicio (`plantilla/preguntas-por-servicio.md`).
3. Resumir en 3 líneas «lo que entendí» y pedir que el cliente diga «sí, eso» antes de cotizar.
4. Marcar **riesgos y supuestos** (qué cuentas debe crear el cliente, qué costos puede tener, qué quedó pendiente).
5. Pasar a `cotizador-servicios` y `alcance-y-entrega`.

## Ideas que el cliente quizá no conoce (proponer cuando encajen)
- **Catálogo web con botón de WhatsApp** (gratis, sin API) antes de un bot completo.
- **Bot en Telegram para la dueña** (avisos de pedidos y resumen del día) aunque los compradores usen WhatsApp.
- **Empezar con un piloto pequeño** de 2 semanas y medir (el bot de `plantilla-bot-negocio` compara canales).
- **Una hoja de Excel o Google Sheets** donde el cliente vea sus pedidos o gastos, antes de pensar en una app.

## Señales de alerta
- «Que haga de todo»: sin límite claro, no hay precio justo. Pedir los 3 casos más frecuentes.
- El cliente no tiene (ni quiere abrir) las cuentas necesarias: sin cuentas propias, los datos de sus compradores terminarían en las de Jeiler.
- Pide guardar datos sensibles (salud, datos de menores) sin saber para qué: parar y mirar `privacidad-habeas-data`.
- Quiere WhatsApp «gratis ilimitado»: explicar el tope gratis de Meta y quién paga el exceso.
