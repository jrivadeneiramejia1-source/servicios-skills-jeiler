"""Pruebas de instalar.sh con una carpeta de destino de mentira. Se saltan si no hay bash."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASH = shutil.which("bash")


@unittest.skipUnless(BASH, "bash no está instalado (en Windows, Git Bash o WSL)")
class TestInstalar(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "repo"
        shutil.copytree(RAIZ, self.repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        self.destino = self.tmp / "destino"

    def correr(self, *args):
        env = {**os.environ, "CLAUDE_SKILLS_DIR": str(self.destino)}
        return subprocess.run([BASH, str(self.repo / "instalar.sh"), *args], capture_output=True, text=True, env=env, timeout=60)

    def test_lista(self):
        r = self.correr("--lista")
        self.assertEqual(r.returncode, 0)
        self.assertIn("comercial:", r.stdout)

    def test_instala_un_grupo_y_marca(self):
        r = self.correr("comercial")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for s in ("briefing-cliente", "cotizador-servicios", "alcance-y-entrega", "oferta-y-portafolio"):
            self.assertTrue((self.destino / s / "SKILL.md").is_file(), s)
            self.assertTrue((self.destino / s / ".instalada-por-skills-jeiler").is_file(), s)

    def test_no_copia_pycache(self):
        """Fallo conocido (PRUEBAS.md): instalar.sh copiaba __pycache__ si existía."""
        cache = self.repo / "skills/cotizador-servicios/scripts/__pycache__"
        cache.mkdir(parents=True)
        (cache / "cotizar.cpython-312.pyc").write_bytes(b"x")
        self.assertEqual(self.correr("comercial").returncode, 0)
        self.assertFalse(list(self.destino.rglob("__pycache__")))
        self.assertTrue((self.destino / "cotizador-servicios/scripts/cotizar.py").is_file())

    def test_no_pisa_una_skill_ajena(self):
        (self.destino / "briefing-cliente").mkdir(parents=True)
        (self.destino / "briefing-cliente/SKILL.md").write_text("ajena", encoding="utf-8")
        r = self.correr("comercial")
        self.assertIn("OMITIDA", r.stdout)
        self.assertEqual((self.destino / "briefing-cliente/SKILL.md").read_text(encoding="utf-8"), "ajena")

    def test_reinstalar_no_falla(self):
        self.assertEqual(self.correr("comercial").returncode, 0)
        self.assertEqual(self.correr("comercial").returncode, 0)

    def test_grupo_inexistente_da_error(self):
        self.assertEqual(self.correr("no-existe").returncode, 1)

    def test_sin_argumentos_da_uso(self):
        self.assertEqual(self.correr().returncode, 1)


if __name__ == "__main__":
    unittest.main()
