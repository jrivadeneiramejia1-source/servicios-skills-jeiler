# Qué se probó de verdad (2026-11-05)

Todo con datos **inventados**. Ninguna plantilla se usó con un cliente real.

## Probado
| Qué | Cómo | Resultado |
|---|---|---|
| Cálculo del cotizador | 12 pruebas (`tests/test_cotizar.py`): ejemplo oficial, colchón, redondeo hacia arriba, descuento, decimales exactos, tarifa mínima, 21 entradas malas (cero, negativos, texto, NaN, infinito, sí/no, descuento fuera de 0–100, etc.), salida en `.md`, archivo roto, sin argumentos | Pasan |
| Skills y repo | 6 pruebas (`tests/test_skills.py`): encabezado YAML válido en las 5 skills, grupos que apuntan a skills que existen, enlaces a plantillas, sin teléfonos ni correos en el repo, avisos legales presentes | Pasan |
| Las pruebas detectan fallas | Se rompió a propósito el encabezado de una skill (descripción con «: » sin comillas) | La prueba falló (bien) y se restauró |
| `instalar.sh` en carpeta limpia | `--lista`, `--activos` dos veces, grupo inexistente | 5 skills instaladas; la segunda vez reinstala sin error; el grupo falso da error (salida 1); el cotizador instalado corre |
| Búsqueda manual de claves y comandos de riesgo | patrones de claves comunes y `eval`, `exec`, `os.system`, `shell=True`, `curl \| sh`, `sudo`, `subprocess`, sockets | 0 hallazgos |

Total: 18 pruebas automáticas, todas pasan.

## Errores encontrados al probar
- El comando `tarifa` chocaba con el archivo de la cotización: `cotizar.py ejemplo.json` fallaba con «invalid choice». Corregido separando los dos usos; hay prueba que lo cubre.
- «1 horas al mes» en el resultado: cambiado a «h al mes».

## NO probado
- **Ninguna plantilla con un cliente real:** briefing, alcance, acta, oferta y portafolio no se han puesto frente a una persona para ver si se entienden.
- **Nada revisado por un abogado ni por un contador.** Las plantillas de privacidad son buenas prácticas, no asesoría legal. Lo que no se verificó (plazos de respuesta, inscripción en el Registro Nacional de Bases de Datos, transferencia internacional, contrato de encargado) está marcado en la skill.
- **La tarifa por hora y las horas de ejemplo son inventadas:** no se compararon con el mercado colombiano.
- Que las skills se activen solas cuando Jeiler pida algo parecido (solo se validó el encabezado, no la activación).
- `gitleaks`: no se pudo instalar en el entorno de la nube; falta correrlo.
- Windows y macOS: solo Linux. `instalar.sh` también copia `__pycache__` si existe (se borra antes de subir).
