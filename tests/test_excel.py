import contextlib
import datetime as dt
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from openpyxl import Workbook, load_workbook

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESC = os.path.join(RAIZ, "skills", "excel-contable", "scripts")
sys.path.insert(0, ESC)
import crear_plantilla  # noqa: E402
import revisar_xlsx  # noqa: E402

def _q(args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return crear_plantilla.main(args)


HAY_LIBREOFFICE = bool(shutil.which("soffice") or shutil.which("libreoffice"))
requiere_lo = unittest.skipUnless(HAY_LIBREOFFICE, "LibreOffice no está instalado: no se puede recalcular")


def calculado(ruta):
    """Abre una copia recalculada por LibreOffice y devuelve el libro con los valores."""
    tmp, rec = revisar_xlsx.recalcular(ruta)
    try:
        wb = load_workbook(rec, data_only=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return wb


def sha(ruta):
    with open(ruta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="test-excel-")
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def ruta(self, nombre):
        return os.path.join(self.dir, nombre)

    def gastos(self, mes="2026-10", extra=None):
        r = self.ruta(f"g-{mes}.xlsx")
        _q(["gastos", r, "--mes", mes, "--inventado"])
        if extra:
            wb = load_workbook(r)
            ws = wb["Movimientos"]
            fila = 2
            while ws.cell(fila, 1).value is not None:
                fila += 1
            for f in extra:
                for c, v in enumerate(f, 1):
                    ws.cell(fila, c, v)
                fila += 1
            wb.save(r)
        return r

    def cartera(self, corte="2026-11-05"):
        r = self.ruta(f"c-{corte}.xlsx")
        _q(["cartera", r, "--corte", corte, "--inventado"])
        return r


@requiere_lo
class Gastos(Base):
    # Cuentas hechas a mano con los datos inventados (octubre): ingresos 850.000 + 420.000; gastos 600.000 + 135.500 + 210.000 + 48.000.
    def test_octubre(self):
        res = calculado(self.gastos())["Resumen"]
        self.assertEqual(res["B3"].value, 1270000)
        self.assertEqual(res["B4"].value, 993500)
        self.assertEqual(res["B5"].value, 276500)
        self.assertEqual(res["B28"].value, 0)
        por_cat = {res[f"A{r}"].value: res[f"B{r}"].value for r in range(8, 28) if res[f"A{r}"].value}
        self.assertEqual(por_cat["Arriendo"], 600000)
        self.assertEqual(por_cat["Servicios públicos"], 135500)
        self.assertEqual(por_cat["Compras"], 210000)
        self.assertEqual(por_cat["Transporte"], 48000)
        self.assertEqual(por_cat["Nómina"], 0)
        self.assertAlmostEqual(res["C8"].value, 600000 / 993500, places=6)

    def test_noviembre_y_bordes_de_mes(self):
        # Un gasto el 1 de noviembre a las 00:00 entra en noviembre y no en octubre; el del 31 de octubre sí está en octubre.
        extra = [(dt.datetime(2026, 11, 1, 0, 0), "Gasto", "Otros gastos", "borde (ejemplo)", 1000)]
        oct_ = calculado(self.gastos("2026-10", extra))["Resumen"]
        self.assertEqual(oct_["B4"].value, 993500)
        nov = calculado(self.gastos("2026-11", extra))["Resumen"]
        self.assertEqual(nov["B3"].value, 300000)
        self.assertEqual(nov["B4"].value, 91000)

    def test_categoria_fuera_de_la_lista_se_ve_en_sin_categoria(self):
        extra = [(dt.date(2026, 10, 20), "Gasto", "Cafetería inventada", "no está en la lista", 50000)]
        res = calculado(self.gastos(extra=extra))["Resumen"]
        self.assertEqual(res["B4"].value, 1043500)
        self.assertEqual(res["B28"].value, 50000)  # la alarma avisa

    def test_mes_vacio_y_sin_divisiones_por_cero(self):
        res = calculado(self.gastos("2025-01"))["Resumen"]
        self.assertEqual((res["B3"].value, res["B4"].value, res["B5"].value, res["B28"].value), (0, 0, 0, 0))
        self.assertIn(res["C8"].value, ("", None))  # sin gastos no hay porcentaje (ni #DIV/0!)

    def test_plantilla_vacia_sin_errores(self):
        r = self.ruta("vacia.xlsx")
        _q(["gastos", r, "--mes", "2026-10"])
        inf = revisar_xlsx.revisar(r, con_recalculo=True)
        self.assertEqual(sum(h["celdas_con_error"] for h in inf["hojas"]), 0)

    def test_hoja_resumen_protegida_con_b1_editable(self):
        wb = load_workbook(self.gastos())
        self.assertTrue(wb["Resumen"].protection.sheet)
        self.assertFalse(wb["Resumen"]["B1"].protection.locked)
        self.assertTrue(wb["Resumen"]["B3"].protection.locked)


@requiere_lo
class Cartera(Base):
    # Cuentas a mano con corte 2026-11-05 (ver crear_plantilla.py):
    #  F-001 vence 31/08, saldo 500.000, mora 66 · F-002 vence 10/10, saldo 200.000, mora 26 · F-003 vence 19/11, saldo 250.000, por vencer
    #  F-004 pagada · F-005 vence 15/07, saldo 80.000, mora 113
    def test_corte_5_de_noviembre(self):
        wb = calculado(self.cartera())
        res, cc = wb["Resumen"], wb["Cuentas por cobrar"]
        self.assertEqual(res["B3"].value, 1030000)
        self.assertEqual(res["B4"].value, 780000)
        self.assertEqual(res["B5"].value, 250000)
        self.assertEqual((res["B8"].value, res["B9"].value, res["B10"].value, res["B11"].value), (200000, 0, 580000, 0))
        self.assertEqual([cc[f"I{r}"].value for r in range(2, 7)], ["Vencida", "Vencida", "Por vencer", "Pagada", "Vencida"])
        self.assertEqual([cc[f"J{r}"].value for r in (2, 3, 6)], [66, 26, 113])
        self.assertEqual(cc["E2"].value.date(), dt.date(2026, 8, 31))

    def test_corte_1_de_diciembre_cambia_la_antiguedad(self):
        res = calculado(self.cartera("2026-12-01"))["Resumen"]
        self.assertEqual(res["B4"].value, 1030000)
        self.assertEqual(res["B5"].value, 0)
        self.assertEqual((res["B8"].value, res["B9"].value, res["B10"].value, res["B11"].value), (250000, 200000, 580000, 0))

    def test_vence_justo_el_dia_de_corte_se_avisa_en_la_revision(self):
        # Vence el 19/11 y el corte es el 19/11: «Por vencer» (no está vencida hoy). La suma por rangos cuadra con el total.
        res = calculado(self.cartera("2026-11-19"))["Resumen"]
        self.assertEqual(res["B3"].value, 1030000)
        self.assertEqual(res["B4"].value - res["B8"].value - res["B9"].value - res["B10"].value, res["B11"].value)

    def test_plantilla_vacia_sin_errores(self):
        r = self.ruta("vacia.xlsx")
        _q(["cartera", r, "--corte", "2026-11-05"])
        inf = revisar_xlsx.revisar(r, con_recalculo=True)
        self.assertEqual(sum(h["celdas_con_error"] for h in inf["hojas"]), 0)


class Plantillas(Base):
    def test_no_pisa_archivos_existentes_ni_acepta_datos_malos(self):
        r = self.ruta("a.xlsx")
        self.assertEqual(_q(["gastos", r]), 0)
        antes = sha(r)
        self.assertEqual(_q(["gastos", r]), 2)
        self.assertEqual(sha(r), antes)
        for args in (["gastos", self.ruta("b.xlsx"), "--mes", "2026-13"], ["gastos", self.ruta("c.xlsx"), "--mes", "hoy"],
                     ["cartera", self.ruta("d.xlsx"), "--corte", "5/11/2026"], ["gastos", self.ruta("e.csv")]):
            with self.subTest(args=args):
                self.assertEqual(_q(args), 2)
        for f in ("b.xlsx", "c.xlsx", "d.xlsx", "e.csv"):
            self.assertFalse(os.path.exists(self.ruta(f)))

    def test_la_plantilla_no_trae_numeros_a_mano_en_columnas_de_formulas(self):
        r = self.ruta("c.xlsx")
        _q(["cartera", r, "--corte", "2026-11-05", "--inventado"])
        for h in revisar_xlsx.revisar(r)["hojas"]:
            self.assertEqual(h["numeros_escritos_a_mano_en_columna_de_formulas"], 0)
            self.assertEqual(h["numeros_guardados_como_texto"], 0)


SECRETO = "CLIENTE-SECRETO-123"
ENCAB_SECRETO = "Cedula-SECRETA-456"


def libro_con_problemas(ruta):
    wb = Workbook()
    ws = wb.active
    ws.title = "Cartera"
    for i, t in enumerate([ENCAB_SECRETO, "Fecha", "Valor", "Total", "Fecha"], 1):  # «Fecha» repetido a propósito
        ws.cell(1, i, t)
    for r in range(2, 8):
        ws.cell(r, 1, f"{SECRETO}-{r}")
        ws.cell(r, 2, dt.date(2026, 10, r))
        ws.cell(r, 3, 1000 * r)
        ws.cell(r, 4, f"=C{r}*1.19")
    ws["B6"] = "05/11/2026"              # fecha como texto
    ws["C5"] = "1.500"                   # número como texto
    ws["D4"] = 777777                    # número escrito a mano en columna de fórmulas
    ws["D7"] = "=1/0"                    # error
    ws["A9"], ws["A10"] = "combinada", None
    ws.merge_cells("A9:B9")
    ws.row_dimensions[3].hidden = True
    ws["F2"] = "=TODAY()"
    ws["G2"] = 5                         # columna G con datos y sin encabezado
    ws["G3"] = 6
    wb.create_sheet("Oculta").sheet_state = "hidden"
    wb.save(ruta)


class Revisor(Base):
    def test_encuentra_los_problemas_sin_mostrar_contenido(self):
        r = self.ruta("problemas.xlsx")
        libro_con_problemas(r)
        antes = sha(r)
        inf = revisar_xlsx.revisar(r, con_recalculo=HAY_LIBREOFFICE)
        h = inf["hojas"][0]
        self.assertEqual(h["numeros_escritos_a_mano_en_columna_de_formulas"], 1)
        self.assertEqual(h["coordenadas_numeros_a_mano"], ["D4"])
        self.assertEqual(h["numeros_guardados_como_texto"], 1)
        self.assertEqual(h["coordenadas_numeros_texto"], ["C5"])
        self.assertEqual(h["fechas_guardadas_como_texto"], 1)
        self.assertEqual(h["coordenadas_fechas_texto"], ["B6"])
        self.assertEqual(h["celdas_combinadas"], 1)
        self.assertEqual(h["filas_ocultas"], 1)
        self.assertEqual(h["encabezados_repetidos"], 1)
        self.assertEqual(h["encabezados_vacios_en_columnas_con_datos"], 2)  # columnas F y G
        self.assertEqual(h["funciones_volatiles"], {"TODAY": 1})
        self.assertEqual(inf["libro"]["hojas_ocultas"], 1)
        if HAY_LIBREOFFICE:
            self.assertEqual(h["coordenadas_error"], ["D7"])
        txt = revisar_xlsx.a_texto(inf)
        for secreto in (SECRETO, ENCAB_SECRETO, "05/11/2026", "777777", "1.500"):
            self.assertNotIn(secreto, txt)
            self.assertNotIn(secreto, str(inf))
        self.assertEqual(sha(r), antes, "el original no se debe modificar")

    def test_sin_recalcular_avisa_que_no_hay_valores_guardados(self):
        r = self.ruta("p.xlsx")
        libro_con_problemas(r)
        h = revisar_xlsx.revisar(r)["hojas"][0]
        self.assertGreater(h["formulas_sin_valor_guardado"], 0)

    def test_encabezados_solo_si_se_piden(self):
        r = self.ruta("p.xlsx")
        libro_con_problemas(r)
        self.assertNotIn("encabezados", revisar_xlsx.revisar(r)["hojas"][0])
        self.assertIn(ENCAB_SECRETO, revisar_xlsx.revisar(r, mostrar_encabezados=True)["hojas"][0]["encabezados"])

    def test_limita_las_coordenadas_listadas(self):
        r = self.ruta("m.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append(["a", "b"])
        for i in range(2, 40):
            ws.cell(i, 1, i)
            ws.cell(i, 2, f"=A{i}*2")
        for i in range(2, 40):
            ws.cell(i, 2).value = i  # 38 números a mano en una columna que era de fórmulas... y se quedó sin ninguna
        for i in range(2, 30):
            ws.cell(i, 2).value = f"=A{i}*2"
        for i in range(30, 40):
            ws.cell(i, 2).value = 5
        wb.save(r)
        h = revisar_xlsx.revisar(r)["hojas"][0]
        self.assertEqual(h["numeros_escritos_a_mano_en_columna_de_formulas"], 10)
        self.assertEqual(len(h["coordenadas_numeros_a_mano"]), 10)
        r2 = self.ruta("m2.xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append(["a", "b"])
        for i in range(2, 60):
            ws.cell(i, 1, i)
            ws.cell(i, 2, f"=A{i}*2" if i < 40 else 5)
        wb.save(r2)
        h = revisar_xlsx.revisar(r2)["hojas"][0]
        self.assertEqual(h["numeros_escritos_a_mano_en_columna_de_formulas"], 20)
        self.assertEqual(len(h["coordenadas_numeros_a_mano"]), 11)  # 10 coordenadas + «y 10 más»
        self.assertTrue(h["coordenadas_numeros_a_mano"][-1].startswith("y 10 más"))

    def test_archivos_malos(self):
        malo = self.ruta("roto.xlsx")
        with open(malo, "wb") as f:
            f.write(b"esto no es un excel")
        csv = self.ruta("datos.csv")
        with open(csv, "w") as f:
            f.write("a,b\n1,2\n")
        for ruta in (malo, csv, self.ruta("no-existe.xlsx")):
            with self.subTest(ruta=ruta):
                with self.assertRaises(ValueError):
                    revisar_xlsx.revisar(ruta)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(revisar_xlsx.main([malo]), 2)

    def test_linea_de_comandos_y_json(self):
        r = self.ruta("p.xlsx")
        libro_con_problemas(r)
        sal = subprocess.run([sys.executable, "-I", os.path.join(ESC, "revisar_xlsx.py"), r, "--json"], capture_output=True, text=True)
        self.assertEqual(sal.returncode, 0)
        self.assertNotIn(SECRETO, sal.stdout)
        self.assertIn('"numeros_escritos_a_mano_en_columna_de_formulas": 1', sal.stdout)


if __name__ == "__main__":
    unittest.main()
