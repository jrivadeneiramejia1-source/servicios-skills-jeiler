# Ejemplo (inventado): Fresas Cremosas Doña Fresa (comida)

> Negocio, nombres y pedidos **inventados** para mostrar el servicio. No es un cliente real.

## El problema
Los pedidos llegan a toda hora y se pierden entre chats; la dueña no sabe cuántos vasos preparar.

## Lo que se hizo
- Un bot de pedidos por **Telegram y WhatsApp** con el catálogo de este negocio (ver `src/negocios/fresas-crema.js` en `plantilla-bot-negocio`).
- Aviso de privacidad al primer mensaje; el comprador puede escribir BORRAR para eliminar sus datos.
- Aviso a la dueña por Telegram de cada pedido y `/resumen` del día con **cuál canal funciona mejor**.
- La nota del pedido sirve para la hora de entrega.

## Cómo se probó
- 26 pruebas automáticas y una conversación completa por cada canal contra el Worker local, con clientes inventados.

## Qué NO se probó
- Una conversación real con WhatsApp o Telegram, y un cliente real usándolo.
- Que Meta acepte el formato exacto de los botones de WhatsApp.

## Qué paga el cliente a terceros
- Cloudflare en nivel gratis. WhatsApp: gratis hasta el tope mensual de Meta; pasado el tope, paga el cliente (confirmar la tarifa vigente).
