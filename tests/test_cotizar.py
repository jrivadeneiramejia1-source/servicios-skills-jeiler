import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from decimal import Decimal

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "skills", "cotizador-servicios", "scripts"))
import cotizar  # noqa: E402

EJEMPLO = os.path.join(RAIZ, "skills", "cotizador-servicios", "ejemplos", "bot-pedidos-ejemplo.json")


def base(**extra):
    d = {"tarifa_hora": 20000, "tareas": [{"nombre": "a", "horas": 8}]}
    d.update(extra)
    return d


class Calculo(unittest.TestCase):
    def test_ejemplo_oficial(self):
        with open(EJEMPLO, encoding="utf-8") as f:
            r = cotizar.calcular(json.load(f))
        self.assertEqual(r["horas_base"], 8)
        self.assertEqual(r["horas_con_colchon"], Decimal("10"))
        self.assertEqual(r["valor_trabajo"], 200000)
        self.assertEqual(r["valor_descuento"], 200000)
        self.assertEqual(r["a_pagar"], 0)
        self.assertEqual(r["mantenimiento"]["cop"], 20000)

    def test_colchon_por_defecto_25(self):
        self.assertEqual(cotizar.calcular(base())["valor_trabajo"], 200000)

    def test_redondea_hacia_arriba_nunca_hacia_abajo(self):
        r = cotizar.calcular({"tarifa_hora": 18333, "tareas": [{"nombre": "a", "horas": 1}], "colchon": 0})
        self.assertEqual(r["valor_trabajo"], 19000)  # 18.333 sube a 19.000

    def test_descuento_parcial(self):
        r = cotizar.calcular(base(descuento_pct=10))
        self.assertEqual(r["valor_descuento"], 20000)
        self.assertEqual(r["a_pagar"], 180000)

    def test_decimales_exactos(self):
        r = cotizar.calcular({"tarifa_hora": 10000, "tareas": [{"nombre": "a", "horas": 0.1}, {"nombre": "b", "horas": 0.2}], "colchon": 0})
        self.assertEqual(r["horas_base"], Decimal("0.3"))  # sin el error 0.30000000000000004 de los decimales binarios
        self.assertEqual(r["valor_trabajo"], 3000)

    def test_tarifa_minima(self):
        self.assertEqual(cotizar.tarifa_hora(1500000, 200000, 60), 29000)  # 28.333 sube a 29.000

    def test_datos_malos(self):
        malos = [
            {}, [], base(tarifa_hora=0), base(tarifa_hora=-5), base(tarifa_hora="abc"), base(tarifa_hora=True),
            base(tarifa_hora="NaN"), base(tarifa_hora="Infinity"), base(tareas=[]), base(tareas=[{"horas": 2}]),
            base(tareas=[{"nombre": "a", "horas": 0}]), base(tareas=[{"nombre": "a", "horas": -1}]),
            base(descuento_pct=101), base(descuento_pct=-1), base(colchon=-0.1), base(colchon=5), base(redondeo=0),
            base(costos_externos=[{"nombre": "x", "cop": 1, "paga": "nadie"}]),
            base(costos_externos=[{"nombre": "x", "cop": -1}]),
            base(costos_externos=[{"nombre": "x", "cop": 1, "periodo": "diario"}]),
            base(mantenimiento_mensual={"horas_mes": 0}),
        ]
        for m in malos:
            with self.subTest(m=m):
                with self.assertRaises(cotizar.ErrorDeDatos):
                    cotizar.calcular(m)

    def test_tarifa_datos_malos(self):
        for args in [(-1, 0, 10), (100, -1, 10), (100, 0, 0), ("x", 0, 10)]:
            with self.subTest(args=args), self.assertRaises(cotizar.ErrorDeDatos):
                cotizar.tarifa_hora(*args)


class Salida(unittest.TestCase):
    def test_markdown_tiene_supuestos_y_descuento(self):
        with open(EJEMPLO, encoding="utf-8") as f:
            md = cotizar.a_markdown(cotizar.calcular(json.load(f)))
        for frase in ["$200.000", "A pagar por el trabajo: $0", "piloto de prueba", "Supuestos", "no son precios de mercado", "consultarlo con un contador"]:
            self.assertIn(frase, md)

    def test_cli(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(cotizar.main([EJEMPLO]), 0)
            self.assertEqual(cotizar.main(["tarifa", "--ingreso", "1500000", "--costos", "200000", "--horas", "60"]), 0)
            self.assertEqual(cotizar.main(["no-existe.json"]), 2)
        self.assertIn("$29.000", out.getvalue())
        self.assertIn("Error:", err.getvalue())

    def test_cli_sin_argumentos_sale_con_2(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as c:
            cotizar.main([])
        self.assertEqual(c.exception.code, 2)

    def test_cli_archivo_roto_y_guardar(self):
        with tempfile.TemporaryDirectory() as t:
            roto = os.path.join(t, "roto.json")
            with open(roto, "w") as f:
                f.write("{no es json")
            salida = os.path.join(t, "c.md")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cotizar.main([roto]), 2)
                self.assertEqual(cotizar.main([EJEMPLO, "--md", salida]), 0)
            self.assertTrue(os.path.getsize(salida) > 100)


if __name__ == "__main__":
    unittest.main()
