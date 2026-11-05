# Qué se probó de verdad (2026-11-05)

Todo con datos **inventados**. Ninguna plantilla se usó con un cliente real.

## Probado
| Qué | Cómo | Resultado |
|---|---|---|
| Cálculo del cotizador | 12 pruebas (`tests/test_cotizar.py`): ejemplo oficial, colchón, redondeo hacia arriba, descuento, decimales exactos, tarifa mínima, 21 entradas malas (cero, negativos, texto, NaN, infinito, sí/no, descuento fuera de 0–100, etc.), salida en `.md`, archivo roto, sin argumentos | Pasan |
| Skills y repo | 6 pruebas (`tests/test_skills.py`): encabezado YAML válido en las 6 skills, grupos que apuntan a skills que existen, enlaces a plantillas, sin teléfonos ni correos en el repo, avisos legales presentes | Pasan |
| Las pruebas detectan fallas | Se rompió a propósito el encabezado de una skill (descripción con «: » sin comillas) | La prueba falló (bien) y se restauró |
| `instalar.sh` en carpeta limpia | `--lista`, `--activos` dos veces, grupo inexistente | 6 skills instaladas (con Excel); la segunda vez reinstala sin error; el grupo falso da error (salida 1); el cotizador instalado corre |
| Búsqueda manual de claves y comandos de riesgo | patrones de claves comunes y `eval`, `exec`, `os.system`, `shell=True`, `curl \| sh`, `sudo`, `subprocess`, sockets | 0 hallazgos |

| **Excel contable** (rama `claude/excel-contable`) | | |
| Plantilla de gastos | 6 pruebas: se calcula con LibreOffice y se compara con cuentas hechas a mano (octubre y noviembre, bordes de mes: 31/10 y 1/11 a las 00:00), categoría fuera de la lista (la fila de control avisa), mes vacío sin errores, plantilla vacía sin errores, hoja protegida con B1 editable | Pasan |
| Plantilla de cuentas por cobrar | 4 pruebas: vencida, por vencer y pagada; días de mora (66, 26, 113); rangos 1-30, 31-60 y 61 o más con dos fechas de corte; los rangos cuadran con el total; plantilla vacía sin errores | Pasan |
| Creador de plantillas | no pisa archivos existentes, rechaza mes, fecha o extensión mal escritos, la plantilla no trae números a mano | Pasan |
| Revisor de archivos (`revisar_xlsx.py`) | libro con problemas puestos a propósito: número a mano, número y fecha como texto, error `#DIV/0!` (con recalculo), celda combinada, fila y hoja ocultas, encabezado repetido, columnas sin encabezado, función `TODAY` | Detecta todo; **el informe no contiene valores ni nombres** (se buscaron nombres y números secretos); el original no cambia (misma huella); archivo roto, `.csv` o inexistente dan error claro |
| Las pruebas de Excel detectan fallas | Se rompió a propósito el borde de mes de la fórmula; aparte, se hizo que el revisor filtrara un valor | En cada caso 1 prueba falló (bien) |

Total: 36 pruebas automáticas, todas pasan (6 de skills, 12 del cotizador y 18 de Excel).

## Errores encontrados al probar
- (Excel) El revisor marcaba como «sin encabezado» una hoja de resumen que no es una tabla; ahora solo lo exige en hojas con 2 o más textos en la fila 1.
- (Excel) Las pruebas del repo detectaron que una skill nueva sin `SKILL.md` ni grupo hace fallar el conjunto, como debe ser.
- El comando `tarifa` chocaba con el archivo de la cotización: `cotizar.py ejemplo.json` fallaba con «invalid choice». Corregido separando los dos usos; hay prueba que lo cubre.
- «1 horas al mes» en el resultado: cambiado a «h al mes».

## NO probado
- **Ninguna plantilla con un cliente real:** briefing, alcance, acta, oferta y portafolio no se han puesto frente a una persona para ver si se entienden.
- **Nada revisado por un abogado ni por un contador.** Las plantillas de privacidad son buenas prácticas, no asesoría legal. Lo que no se verificó (plazos de respuesta, inscripción en el Registro Nacional de Bases de Datos, transferencia internacional, contrato de encargado) está marcado en la skill.
- **La tarifa por hora y las horas de ejemplo son inventadas:** no se compararon con el mercado colombiano.
- **Excel:** nada se abrió en Microsoft Excel ni en Google Sheets (solo LibreOffice); los nombres de funciones en español, la protección de hojas y las listas desplegables pueden comportarse distinto. No se probó con un archivo real de un cliente ni con archivos grandes (más de 2.000 filas en gastos o 500 en cuentas por cobrar: las fórmulas no cubren más; hay que ampliarlas).
- Que las skills se activen solas cuando Jeiler pida algo parecido (solo se validó el encabezado, no la activación).
- `gitleaks`: no se pudo instalar en el entorno de la nube; falta correrlo.
- Windows y macOS: solo Linux. `instalar.sh` también copia `__pycache__` si existe (se borra antes de subir).
