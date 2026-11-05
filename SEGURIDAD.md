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
- `gitleaks` **no se pudo instalar** en el entorno de la nube. Pendiente correrlo en un computador que lo tenga.

## Lo legal
- Las plantillas de privacidad son prácticas, **no asesoría legal**. Lo no verificado está marcado en `skills/privacidad-habeas-data/SKILL.md`. Un abogado debe revisarlas antes de usarlas con clientes reales.
