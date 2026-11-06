# Seguridad y privacidad

## Reglas
- Repo público: sin datos de clientes ni de sus compradores. `.gitignore` bloquea `.xlsx`, `.csv`, `.pdf`, `clientes/`, `privado/` y `cotizaciones-reales/` como red de seguridad; no reemplaza la revisión a mano antes de cada commit.
- Sin claves, tokens ni contraseñas. Las plantillas dicen que las claves nunca se escriben en papeles ni chats.
- Los datos de clientes (Excel contables, correos, teléfonos) no se pegan en chats con IA ni se mandan a servicios externos sin permiso de su dueño.
- Archivos de comunidades indígenas: no se modifican ni se suben a servicios externos.

## Código
- `cotizar.py`: solo librería estándar de Python, no abre redes, no ejecuta comandos, solo lee el JSON que se le da y escribe el `.md` que se le pide.
- `crear_plantilla.py` y `revisar_xlsx.py` (Excel): usan `openpyxl` (MIT, se instala al usarlos). No abren redes. `revisar_xlsx.py --recalcular` llama a LibreOffice (`soffice`, sin internet, argumentos fijos, sin shell) sobre una **copia temporal** que borra al terminar; el original nunca se escribe. El informe del revisor solo trae cantidades y coordenadas, no valores.
- Sin código de terceros copiado.

## Revisión (2026-11-05)
- Búsqueda manual de patrones de claves y de comandos de riesgo (`eval`, `exec`, `os.system`, `shell=True`, `curl | sh`, `sudo`): ver `PRUEBAS.md`.
- **gitleaks 8.30.0 corrido el 2026-11-06** (descargado del sitio oficial, checksum `OK`, sobre los archivos del repo; el clon era superficial y no incluye el historial). Primera pasada: **1 hallazgo**, un falso positivo en `tests/test_excel.py` (un texto inventado, «Cedula-SECRETA-456», guardado en una constante llamada `ENCAB_SECRETO`, que sirve para probar que el revisor de Excel no muestra valores). Se renombraron las constantes de prueba y quedó en **0 hallazgos**. **Historial completo (5 commits) corrido el 2026-11-06:** 1 hallazgo, el mismo texto inventado en `tests/test_excel.py` tal como estaba antes de renombrar la constante (ficticio; ninguno real).

## Lo legal
- Las plantillas de privacidad son prácticas, **no asesoría legal**. Lo no verificado está marcado en `skills/privacidad-habeas-data/SKILL.md`. Un abogado debe revisarlas antes de usarlas con clientes reales.

## Flujo de pruebas automáticas (2026-11-06)
`.github/workflows/pruebas.yml` corre las pruebas en cada pull request y en `main`: permisos de solo lectura, sin secretos, `actions/checkout` fijado a un commit con `persist-credentials: false`, y `openpyxl` y `pyyaml` (MIT) instalados en un entorno aparte. Revisado con actionlint 1.7.12 y zizmor 1.32.0 (modo pedante): 0 hallazgos.
