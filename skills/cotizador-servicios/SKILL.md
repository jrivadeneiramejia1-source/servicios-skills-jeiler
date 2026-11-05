---
name: cotizador-servicios
description: >-
  Calcula en pesos colombianos cuánto cobrar por un servicio (bot de WhatsApp o Telegram, apoyo con Excel, app web o APK, video) a partir de las horas de trabajo, una tarifa por hora, un colchón por imprevistos y los costos de terceros, y muestra aparte el descuento cuando es un piloto gratis. Usar cuando Jeiler diga "cuánto cobro", "hazme una cotización", "cuánto le pongo a esto" o "precio para un cliente". No inventa precios de mercado: todo número es un supuesto que Jeiler escribe y queda marcado.
---

# Cotizador de servicios (COP)

Convierte «cuánto trabajo es» en «cuánto cobrar», con la cuenta a la vista. Sirve igual para un cliente que paga y para un piloto gratis (se ve el valor que se regala).

## Reglas
- **Nunca inventar precios de mercado.** La tarifa por hora, las horas y el colchón los pone Jeiler; el resultado dice que son supuestos.
- **Costos de terceros aparte** (Cloudflare, Meta, dominios): los paga el cliente con sus propias cuentas y no son ganancia de Jeiler. Verificar su valor vigente el día de cotizar.
- Cotizar por **alcance cerrado** (lista de tareas). Lo que no esté en la lista se cotiza aparte (ver `alcance-y-entrega`).
- Alias del cliente, nunca nombres ni datos reales dentro de este repo (es público). Las cotizaciones reales se guardan fuera del repo.
- Impuestos y factura: depende de cómo esté registrado Jeiler. No es asesoría; que lo confirme un contador.

## Proceso
1. **Tarifa por hora** (si aún no la tiene): `python3 scripts/cotizar.py tarifa --ingreso 1500000 --costos 200000 --horas 60`. Es una cuenta: (lo que quiere ganar + sus gastos) ÷ horas que de verdad puede cobrar al mes. Compararla con lo que cobran otros en su zona; **las cifras del ejemplo son inventadas**.
2. **Copiar** `ejemplos/bot-pedidos-ejemplo.json` y cambiar: tareas con horas, tarifa, colchón (25 % por defecto: el trabajo siempre se demora más), costos de terceros, descuento y mantenimiento mensual.
3. **Calcular:** `python3 scripts/cotizar.py mi-cotizacion.json --md cotizacion.md`. Redondea hacia arriba a 1.000 pesos.
4. **Revisar con ojos críticos:** ¿faltan tareas (pruebas, explicarle al cliente, cuentas)? ¿el cliente entiende qué NO incluye? Ajustar y recalcular.
5. Enviar la cotización junto con el alcance (`alcance-y-entrega`).

## Para los pilotos gratis (clientas conocidas)
Poner `"descuento_pct": 100` y `"descuento_motivo"`. Así queda escrito cuánto valía el trabajo, y cuando termine el piloto se puede cobrar con ese mismo cálculo.

## Señales de alerta
- Cobrar por horas sueltas sin lista de tareas: el cliente siempre pide «una cosita más».
- Prometer «gratis para siempre»: WhatsApp y Cloudflare tienen topes; pasado el tope paga el cliente a ellos.
- Una tarifa sacada de la nada: usar el comando `tarifa` y compararla con el mercado.

## Qué se probó
Ver `PRUEBAS.md` del repo: 12 pruebas automáticas del cálculo (redondeo, decimales, datos malos, salida). **No** se comparó la tarifa con el mercado.
