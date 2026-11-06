---
name: excel-contable
description: >-
  Apoyo con Excel para áreas administrativas y contables de pequeños negocios: crea plantillas con fórmulas verificadas (ingresos y gastos por mes, cuentas por cobrar con vencimiento y antigüedad), revisa archivos de clientes sin mostrar su contenido (errores de fórmulas, números o fechas guardados como texto, celdas combinadas, hojas ocultas) y explica cómo trabajar con archivos reales sin filtrar datos. Usar cuando Jeiler diga "hazme un Excel de gastos", "cuentas por cobrar", "arregla este Excel", "un cliente me mandó un Excel", "Excel contable" o "automatizar una hoja". No da asesoría contable ni tributaria.
---

# Excel contable y administrativo

Para vender apoyo con Excel sin regalar los datos de nadie ni entregar hojas que fallan en silencio. Se apoya en la skill `xlsx` de la cuenta para el trabajo pesado con archivos; esta aporta las reglas, las plantillas probadas y el revisor que no muestra datos.

## Reglas
- **Una IA es un servicio externo.** Pegar o subir el contenido de un Excel real a un chat con IA es mandarlo a un tercero. Solo con **permiso escrito de su dueño** (`privacidad-habeas-data`). Por defecto: trabajar con una estructura inventada y usar `revisar_xlsx.py`, que corre en tu computador y solo entrega cantidades y coordenadas.
- **Nunca modificar el original:** se trabaja en una copia y se entrega un archivo nuevo. Los archivos reales no entran a repos (el repo es público; `.gitignore` bloquea `.xlsx`, `.csv` y `.pdf`).
- **Fórmulas, no números escritos a mano**, con una fila o celda de **control** que avise cuando algo no cuadra (por ejemplo «sin categoría»).
- **No dar asesoría contable ni tributaria** (IVA, retenciones, renta, DIAN): lo valida el contador del cliente. Las plantillas organizan datos; no declaran impuestos.
- Datos de ejemplo siempre inventados («Cliente de ejemplo A»).
- Decir qué no se probó: solo se calculó con LibreOffice; **no** se abrió en Excel ni en Google Sheets.

## Proceso
1. **Entender** (`briefing-cliente`, preguntas de Excel): qué se hace a mano, cuántas filas, quién edita, qué reportes necesita.
2. **Plantilla de arranque** (opcional): `python scripts/crear_plantilla.py gastos salida.xlsx --inventado` o `cartera`. Sale con listas desplegables, validación de fechas y valores, resumen protegido (sin clave: solo evita borrar fórmulas por accidente) y celdas amarillas para escribir. Sin `--inventado` sale vacía.
3. **Si el cliente ya tiene un archivo:** pedir permiso, copiarlo y correr `python scripts/revisar_xlsx.py copia.xlsx --recalcular`. Con ese informe (sin datos) se sabe qué arreglar. Los nombres de las columnas solo se muestran con `--mostrar-encabezados`; revisarlos antes de compartirlos.
4. **Construir o arreglar** en la copia. Reglas de oro: una fila por movimiento (nada de celdas combinadas), una columna por dato, fechas como fechas y números como números, listas para lo que se repite.
5. **Verificar de verdad:** calcular con LibreOffice (`--recalcular`), comparar con una **cuenta hecha aparte** sobre datos inventados, probar los bordes (último y primer día del mes, mes vacío, categoría que no está en la lista) y mirar el archivo con ojos críticos.
6. **Entregar** con `alcance-y-entrega`: archivo nuevo, qué incluye y qué no, y qué se probó. Borrar las copias de datos del cliente.

## Notas prácticas
- Las fórmulas se guardan con nombres en inglés; Excel en español las muestra traducidas (por ejemplo `SUMIFS` aparece como `SUMAR.SI.CONJUNTO`). El archivo funciona igual.
- Si se pide **automatizar** (enviar correos, copiar filas) en Google Sheets: Apps Script es gratis; en cuenta gmail.com limita cada ejecución a 6 minutos y los correos a 100 destinatarios por día (según su página de cuotas, 2026-11-05; Google dice que pueden cambiar). El bot de `plantilla-bot-negocio` ya usa Apps Script para copiar pedidos.
- La DIAN ofrece facturación electrónica gratuita (requiere RUT y certificado); esta skill no la reemplaza ni la automatiza.

## Señales de alerta
- Que el cliente mande por chat el Excel con cédulas, cuentas o nómina «para que lo arregles».
- Totales escritos a mano o fórmulas que apuntan a rangos fijos que dejan datos nuevos por fuera (por eso las plantillas cubren 2.000 y 500 filas y traen una fila de control).
- Prometer que «cumple con la DIAN» o que «el IVA está bien».
- Entregar sin haber comparado el resultado con una cuenta hecha aparte.

## Qué se probó
Ver `PRUEBAS.md`: las plantillas se calcularon con LibreOffice y se compararon con cuentas hechas a mano; el revisor se probó con un libro lleno de problemas y se comprobó que no deja salir contenido. **No** se probó en Excel ni en Google Sheets, ni con un archivo real de un cliente.
