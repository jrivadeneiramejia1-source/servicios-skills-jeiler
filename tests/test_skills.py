import os
import re
import unittest

import yaml

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(RAIZ, "skills")


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def todas():
    return sorted(d for d in os.listdir(SKILLS) if os.path.isdir(os.path.join(SKILLS, d)))


class Skills(unittest.TestCase):
    def test_hay_cinco_skills(self):
        self.assertEqual(len(todas()), 5)

    def test_frontmatter_yaml_valido(self):
        # Lección aprendida: un "description:" con ": " sin comillas rompe el YAML (12 skills ya fallaron).
        for s in todas():
            with self.subTest(skill=s):
                t = leer(os.path.join(SKILLS, s, "SKILL.md"))
                m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
                self.assertIsNotNone(m, "sin bloque de encabezado")
                datos = yaml.safe_load(m.group(1))
                self.assertEqual(datos["name"], s)
                self.assertIsInstance(datos["description"], str)
                self.assertGreater(len(datos["description"]), 80)

    def test_grupos_apuntan_a_skills_que_existen(self):
        lineas = [l for l in leer(os.path.join(RAIZ, "grupos.conf")).splitlines() if l.strip() and not l.startswith("#")]
        usadas = set()
        grupos = set()
        for l in lineas:
            g, resto = l.split(":", 1)
            grupos.add(g)
            for s in resto.split():
                self.assertIn(s, todas(), f"{s} (grupo {g}) no existe")
                usadas.add(s)
        self.assertEqual(usadas, set(todas()), "hay skills fuera de todo grupo")
        for g in [l.strip() for l in leer(os.path.join(RAIZ, "grupos-activos.txt")).splitlines() if l.strip() and not l.startswith("#")]:
            self.assertIn(g, grupos)

    def test_enlaces_entre_skills_y_archivos(self):
        for s in todas():
            t = leer(os.path.join(SKILLS, s, "SKILL.md"))
            for ref in re.findall(r"`(plantilla/[\w.-]+)`", t):
                self.assertTrue(os.path.exists(os.path.join(SKILLS, s, ref)), f"{s}: falta {ref}")
            for otra in re.findall(r"`(briefing-cliente|cotizador-servicios|alcance-y-entrega|oferta-y-portafolio|privacidad-habeas-data)`", t):
                self.assertIn(otra, todas())

    def test_plantillas_no_traen_datos_reales(self):
        patrones = [r"\b3\d{9}\b", r"\b\d{1,3}(\.\d{3}){2}\b(?!\s*pesos)", r"[\w.+-]+@[\w-]+\.[\w.]+", r"https?://wa\.me/\d+"]
        for raiz, _, archivos in os.walk(RAIZ):
            if ".git" in raiz.split(os.sep):
                continue
            for a in archivos:
                if not a.endswith((".md", ".json", ".py")) or a == "test_skills.py":
                    continue
                t = leer(os.path.join(raiz, a))
                for p in patrones[:1] + patrones[2:]:
                    self.assertIsNone(re.search(p, t), f"{a}: parece un dato personal ({p})")

    def test_las_skills_advierten_lo_legal_y_lo_no_probado(self):
        t = leer(os.path.join(SKILLS, "privacidad-habeas-data", "SKILL.md"))
        self.assertIn("no es asesoría legal", t.lower())
        self.assertIn("confirmar", t)


if __name__ == "__main__":
    unittest.main()
