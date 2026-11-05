# servicios-skills-jeiler

Skills para **ofrecer y entregar** servicios (bots de WhatsApp y Telegram, apoyo con Excel, apps, videos) con orden: entender al cliente, cotizar en pesos colombianos, dejar el alcance por escrito, cuidar los datos de las personas y presentar un portafolio con ejemplos inventados.

Repo **público**: nada de datos de clientes ni de sus compradores. Las plantillas están vacías y los ejemplos son inventados.

| Skill | Para qué |
|---|---|
| `briefing-cliente` | Entender qué necesita el cliente (12 preguntas + preguntas por servicio) |
| `cotizador-servicios` | Calcular cuánto cobrar en pesos, con la cuenta a la vista (script probado) |
| `alcance-y-entrega` | Qué incluye y qué no, cambios incluidos, acta de entrega (pagado o piloto) |
| `excel-contable` | Plantillas de Excel con fórmulas probadas y revisor de archivos que no muestra datos |
| `privacidad-habeas-data` | Ley 1581 explicada simple, aviso del bot, política y lista de revisión |
| `oferta-y-portafolio` | Oferta de una página y portafolio con casos inventados |

El bot de pedidos vive en `plantilla-bot-negocio`. Estado y lo que falta: `docs/ESTADO-servicios.md`.

## Instalar
```bash
./instalar.sh --lista        # ver los grupos
./instalar.sh comercial      # copia las skills a ~/.claude/skills (o a $CLAUDE_SKILLS_DIR)
```

## Probar
```bash
pip install openpyxl            # para las plantillas y el revisor de Excel
python3 -I -m unittest discover -s tests
```
Las pruebas que calculan fórmulas usan LibreOffice (`soffice`); si no está, esas se saltan y lo dicen.

Aviso: nada de lo legal está revisado por un abogado ni lo comercial por un contador. Ver `PRUEBAS.md` y `SEGURIDAD.md`. Licencia MIT.
