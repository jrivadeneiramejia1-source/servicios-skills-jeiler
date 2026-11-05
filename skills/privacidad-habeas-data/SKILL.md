---
name: privacidad-habeas-data
description: >-
  Explica en palabras simples cómo cuidar los datos personales de los clientes y de sus compradores según la Ley 1581 de 2012 (habeas data) en Colombia y deja listos un aviso de privacidad para el bot, una autorización y una lista de revisión: qué datos se piden, para qué, quién es responsable, cómo se borran, qué pasa con los servidores fuera del país. Usar cuando Jeiler diga "habeas data", "Ley 1581", "aviso de privacidad", "datos de mis clientes", "puedo guardar teléfonos", "archivos de Excel de un cliente" o antes de entregar un bot, una app o un Excel que guarde datos de personas. No es asesoría legal: lo que no está verificado queda marcado.
---

# Privacidad y habeas data (Colombia)

**Idea simple:** los datos de una persona (nombre, teléfono, dirección, qué compró) son de ella, no de quien los guarda. Quien los pide debe decir para qué, pedir permiso, cuidarlos y borrarlos si se lo piden.

> **Esto no es asesoría legal.** Es una guía práctica de buenas costumbres basada en lo que Jeiler sabe de la Ley 1581 de 2012. Lo marcado **«confirmar»** no se verificó en una fuente oficial: antes de vender, que lo revise un abogado o consulte la página de la Superintendencia de Industria y Comercio (SIC), que es quien vigila esta ley.

## Reglas para Jeiler
- **Datos de clientes** (Excel contables, correos, teléfonos, pedidos): nunca a un repo (es público), nunca a servicios externos ni a chats con IA sin permiso de su dueño. Para practicar, datos inventados.
- Los datos de los compradores de un negocio viven en **las cuentas del negocio** (su Cloudflare, su Meta, su Google), no en las de Jeiler.
- **No pedir lo que no hace falta.** El bot de pedidos pide nombre, nota de entrega y contacto; nada más.
- **No guardar datos sensibles** (salud, origen étnico, creencias, vida sexual, datos biométricos) ni **datos de niños y adolescentes** sin asesoría. Si un negocio los necesita, parar y consultar.
- Archivos de comunidades indígenas: irreemplazables; nunca se modifican ni se suben a servicios externos.

## Quién es quién (confirmar con abogado)
- **Responsable:** el negocio dueño de los compradores; decide para qué se usan los datos.
- **Encargado:** quien los maneja por cuenta del negocio. Si Jeiler configura un bot o mantiene un Excel con datos del cliente, es **encargado** y conviene dejarlo escrito en el alcance (`alcance-y-entrega`).

## Lo que debe tener un buen manejo de datos
1. **Autorización previa:** el comprador acepta antes de que se guarde nada (el bot lo hace con «Acepto»).
2. **Decir para qué** se usan los datos y que no se comparten.
3. **Derechos del dueño del dato** (confirmar los detalles): conocer qué se guarda, corregirlo, pedir que se borre, retirar el permiso y quejarse ante la SIC. El bot permite borrar con la palabra BORRAR.
4. **Guardar poco tiempo:** el bot borra sesiones viejas a los 7 días; los pedidos se conservan sin nombre ni contacto si la persona pide borrar.
5. **Seguridad:** claves como secretos, nada en repos, nada por chat.
6. **Servidores fuera de Colombia:** Cloudflare, Telegram y Meta guardan datos en otros países. Hay que **decirlo** en el aviso y revisar con un abogado si hace falta algo más (transferencia internacional de datos: **confirmar**).
7. **Política de tratamiento:** un texto corto y público del negocio que diga todo lo anterior. La plantilla está en `plantilla/politica-tratamiento.md`.

## Cosas que NO se verificaron (confirmar antes de afirmarlas a un cliente)
- Plazos exactos para responder consultas y reclamos de los dueños de los datos.
- Si un negocio pequeño debe inscribir sus bases en el Registro Nacional de Bases de Datos (RNBD): según lo que Jeiler recuerda, solo aplica a empresas grandes, pero **confirmar con la SIC**.
- Si el nivel de protección de los países donde están los servidores basta o se necesita una autorización especial.
- Cuándo Jeiler necesita su propio contrato de encargado con cada cliente.

## Proceso
1. Con el briefing (`briefing-cliente`, pregunta 7), listar **qué datos** y **para qué**.
2. Ajustar `plantilla/aviso-bot.md` (es el que el bot muestra) y `plantilla/politica-tratamiento.md` al negocio.
3. Pasar la lista de revisión de `plantilla/lista-revision.md` antes de entregar.
4. Si hay datos sensibles, de menores o archivos contables reales: parar y recomendar un abogado o contador.

## Señales de alerta
- Pegar en un chat con IA un Excel con nombres, cédulas o cuentas reales.
- Un bot que guarda todo «por si acaso».
- Cuentas de Jeiler como dueñas de los datos de los compradores de un cliente.
- Decir «cumple la ley»: lo correcto es «sigue buenas prácticas; que un abogado lo confirme».
