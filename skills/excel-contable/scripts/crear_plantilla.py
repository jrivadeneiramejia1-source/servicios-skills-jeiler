#!/usr/bin/env python3
"""Crea plantillas de Excel con FÓRMULAS (no números escritos a mano) para apoyo administrativo y contable.

  python crear_plantilla.py gastos   salida.xlsx [--mes 2026-10] [--inventado]
  python crear_plantilla.py cartera  salida.xlsx [--corte 2026-11-05] [--inventado]

  gastos : ingresos y gastos por mes, con resumen por categoría y una revisión de «sin categoría».
  cartera: cuentas por cobrar con vencimiento, estado y antigüedad de la deuda (1-30, 31-60, 61 o más días).

--inventado llena algunas filas con datos de mentira (para enseñar o probar). Sin esa opción la plantilla sale vacía.
Sin --mes / --corte se usa la fecha de hoy (fórmula HOY), y se puede cambiar escribiendo otra fecha en la celda B1 del Resumen.
Requiere: pip install openpyxl
"""
import argparse
import datetime as dt
import sys

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill, Protection
from openpyxl.worksheet.datavalidation import DataValidation

FILAS = 2000          # filas con fórmulas/validaciones en las hojas de datos
FILAS_CARTERA = 500
CATEGORIAS = ["Arriendo", "Servicios públicos", "Transporte", "Compras", "Nómina", "Impuestos", "Ventas", "Otros ingresos", "Otros gastos"]
PESOS = '"$"#,##0'
FECHA = "dd/mm/yyyy"
ENC = PatternFill("solid", fgColor="DDEBF7")
ENTRADA = PatternFill("solid", fgColor="FFF2CC")  # celdas que se escriben
NEGRITA = Font(bold=True)


def encabezados(ws, titulos, anchos):
    for i, (t, a) in enumerate(zip(titulos, anchos), 1):
        c = ws.cell(1, i, t)
        c.font, c.fill = NEGRITA, ENC
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[c.column_letter].width = a
    ws.freeze_panes = "A2"


def fecha_celda(ws, ref, valor, formula_hoy):
    ws[ref] = valor if valor else formula_hoy
    ws[ref].number_format = FECHA
    ws[ref].fill = ENTRADA


def plantilla_gastos(ruta, mes, inventado):
    wb = Workbook()
    mov = wb.active
    mov.title = "Movimientos"
    encabezados(mov, ["Fecha", "Tipo", "Categoría", "Descripción", "Valor (COP)"], [13, 11, 24, 40, 16])
    listas = wb.create_sheet("Listas")
    listas["A1"], listas["A1"].font, listas["A1"].fill = "Categorías (puedes cambiarlas)", NEGRITA, ENC
    listas.column_dimensions["A"].width = 32
    for i, c in enumerate(CATEGORIAS, 2):
        listas.cell(i, 1, c).fill = ENTRADA

    dv_tipo = DataValidation(type="list", formula1='"Ingreso,Gasto"', allow_blank=True, showErrorMessage=True, errorTitle="Tipo", error="Elige Ingreso o Gasto")
    dv_cat = DataValidation(type="list", formula1="=Listas!$A$2:$A$21", allow_blank=True, showErrorMessage=True, errorTitle="Categoría", error="Elige una categoría de la lista (o agrégala en la hoja Listas)")
    dv_fecha = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True, showErrorMessage=True, errorTitle="Fecha", error="Escribe una fecha válida")
    dv_val = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True, showErrorMessage=True, errorTitle="Valor", error="Escribe un número positivo; el Tipo dice si es ingreso o gasto")
    for dv, col in ((dv_fecha, "A"), (dv_tipo, "B"), (dv_cat, "C"), (dv_val, "E")):
        mov.add_data_validation(dv)
        dv.add(f"{col}2:{col}{FILAS}")
    for r in range(2, FILAS + 1):
        mov.cell(r, 1).number_format = FECHA
        mov.cell(r, 5).number_format = PESOS

    res = wb.create_sheet("Resumen", 0)
    res["A1"], res["A1"].font = "Mes a revisar (cualquier día de ese mes)", NEGRITA
    fecha_celda(res, "B1", dt.date(mes[0], mes[1], 1) if mes else None, "=DATE(YEAR(TODAY()),MONTH(TODAY()),1)")
    ini = "DATE(YEAR($B$1),MONTH($B$1),1)"
    fin = f"EDATE({ini},1)"
    rango = lambda col: f"Movimientos!${col}$2:${col}${FILAS}"
    crit_mes = f'{rango("A")},">="&{ini},{rango("A")},"<"&{fin}'
    res["A3"], res["A4"], res["A5"] = "Ingresos del mes", "Gastos del mes", "Saldo del mes"
    res["B3"] = f'=SUMIFS({rango("E")},{rango("B")},"Ingreso",{crit_mes})'
    res["B4"] = f'=SUMIFS({rango("E")},{rango("B")},"Gasto",{crit_mes})'
    res["B5"] = "=B3-B4"
    for r in (3, 4, 5):
        res[f"A{r}"].font = NEGRITA
        res[f"B{r}"].number_format = PESOS
    res["A7"], res["B7"], res["C7"] = "Gastos por categoría", "Valor", "% de los gastos"
    for c in ("A7", "B7", "C7"):
        res[c].font, res[c].fill = NEGRITA, ENC
    for i in range(20):
        r = 8 + i
        res[f"A{r}"] = f'=IF(Listas!A{i + 2}="","",Listas!A{i + 2})'
        res[f"B{r}"] = f'=IF(A{r}="","",SUMIFS({rango("E")},{rango("B")},"Gasto",{rango("C")},A{r},{crit_mes}))'
        res[f"C{r}"] = f'=IF(OR(A{r}="",$B$4=0),"",B{r}/$B$4)'
        res[f"B{r}"].number_format = PESOS
        res[f"C{r}"].number_format = "0.0%"
    res["A28"] = "Sin categoría o con una que no está en la lista"
    res["B28"] = "=B4-SUM(B8:B27)"
    res["B28"].number_format = PESOS
    res["A29"] = "Si B28 no es cero, hay gastos que no entran en ninguna categoría de arriba: revísalos."
    res["A29"].font = Font(italic=True, color="7F7F7F")
    res.column_dimensions["A"].width = 46
    res.column_dimensions["B"].width = 18
    res.column_dimensions["C"].width = 16
    res.conditional_formatting.add("B5", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="C00000", bold=True)))
    res.conditional_formatting.add("B28", CellIsRule(operator="notEqual", formula=["0"], fill=PatternFill("solid", bgColor="F8CBAD")))
    res.protection.sheet = True  # sin clave: evita borrar fórmulas por accidente; en B1 se puede escribir
    res["B1"].protection = Protection(locked=False)

    if inventado:
        filas = [
            (dt.date(2026, 10, 3), "Ingreso", "Ventas", "Venta de ejemplo 1", 850000),
            (dt.date(2026, 10, 9), "Ingreso", "Ventas", "Venta de ejemplo 2", 420000),
            (dt.date(2026, 10, 15), "Gasto", "Arriendo", "Arriendo del local (ejemplo)", 600000),
            (dt.date(2026, 10, 18), "Gasto", "Servicios públicos", "Luz e internet (ejemplo)", 135500),
            (dt.date(2026, 10, 22), "Gasto", "Compras", "Materiales (ejemplo)", 210000),
            (dt.date(2026, 10, 31), "Gasto", "Transporte", "Domicilios (ejemplo)", 48000),
            (dt.date(2026, 11, 2), "Ingreso", "Ventas", "Venta de ejemplo 3", 300000),
            (dt.date(2026, 11, 4), "Gasto", "Compras", "Materiales noviembre (ejemplo)", 90000),
        ]
        for r, f in enumerate(filas, 2):
            for c, v in enumerate(f, 1):
                mov.cell(r, c, v)
    wb.save(ruta)


def plantilla_cartera(ruta, corte, inventado):
    wb = Workbook()
    cc = wb.active
    cc.title = "Cuentas por cobrar"
    encabezados(cc, ["Cliente (alias)", "Factura", "Fecha de emisión", "Plazo (días)", "Vence", "Valor", "Abonado", "Saldo", "Estado", "Días de mora"], [24, 12, 15, 11, 13, 15, 15, 15, 12, 12])
    res = wb.create_sheet("Resumen", 0)
    res["A1"], res["A1"].font = "Fecha de corte", NEGRITA
    fecha_celda(res, "B1", corte, "=TODAY()")
    dv_f = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True, showErrorMessage=True, errorTitle="Fecha", error="Escribe una fecha válida")
    dv_n = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True, showErrorMessage=True, errorTitle="Número", error="Escribe un número positivo")
    cc.add_data_validation(dv_f)
    cc.add_data_validation(dv_n)
    dv_f.add(f"C2:C{FILAS_CARTERA}")
    for col in "DFG":
        dv_n.add(f"{col}2:{col}{FILAS_CARTERA}")
    for r in range(2, FILAS_CARTERA + 1):
        cc[f"E{r}"] = f'=IF(OR(C{r}="",D{r}=""),"",C{r}+D{r})'
        cc[f"H{r}"] = f'=IF(F{r}="","",F{r}-G{r})'
        cc[f"I{r}"] = f'=IF(H{r}="","",IF(H{r}<=0,"Pagada",IF(AND(E{r}<>"",E{r}<Resumen!$B$1),"Vencida","Por vencer")))'
        cc[f"J{r}"] = f'=IF(I{r}="Vencida",Resumen!$B$1-E{r},"")'
        for col in "CE":
            cc[f"{col}{r}"].number_format = FECHA
        for col in "FGH":
            cc[f"{col}{r}"].number_format = PESOS
    rng = lambda col: f"'Cuentas por cobrar'!${col}$2:${col}${FILAS_CARTERA}"
    res["A3"], res["B3"] = "Total por cobrar", f'=SUMIFS({rng("H")},{rng("I")},"Vencida")+SUMIFS({rng("H")},{rng("I")},"Por vencer")'
    res["A4"], res["B4"] = "   Vencido", f'=SUMIFS({rng("H")},{rng("I")},"Vencida")'
    res["A5"], res["B5"] = "   Por vencer", f'=SUMIFS({rng("H")},{rng("I")},"Por vencer")'
    res["A7"], res["B7"] = "Antigüedad de lo vencido", "Valor"
    for c in ("A7", "B7"):
        res[c].font, res[c].fill = NEGRITA, ENC
    res["A8"], res["B8"] = "1 a 30 días", f'=SUMIFS({rng("H")},{rng("I")},"Vencida",{rng("J")},">=1",{rng("J")},"<=30")'
    res["A9"], res["B9"] = "31 a 60 días", f'=SUMIFS({rng("H")},{rng("I")},"Vencida",{rng("J")},">=31",{rng("J")},"<=60")'
    res["A10"], res["B10"] = "61 días o más", f'=SUMIFS({rng("H")},{rng("I")},"Vencida",{rng("J")},">=61")'
    res["A11"], res["B11"] = "Vencido sin contar (revisar: vence hoy o sin fecha)", "=B4-SUM(B8:B10)"
    for r in (3, 4, 5, 8, 9, 10, 11):
        res[f"B{r}"].number_format = PESOS
    res["A3"].font = NEGRITA
    res["A12"] = "Si B11 no es cero, hay saldos vencidos que no caen en ningún rango: revísalos."
    res["A12"].font = Font(italic=True, color="7F7F7F")
    res.column_dimensions["A"].width = 52
    res.column_dimensions["B"].width = 18
    res.conditional_formatting.add("B11", CellIsRule(operator="notEqual", formula=["0"], fill=PatternFill("solid", bgColor="F8CBAD")))
    res.protection.sheet = True
    res["B1"].protection = Protection(locked=False)

    if inventado:
        filas = [
            ("Cliente de ejemplo A", "F-001", dt.date(2026, 8, 1), 30, 500000, 0),
            ("Cliente de ejemplo B", "F-002", dt.date(2026, 9, 10), 30, 300000, 100000),
            ("Cliente de ejemplo C", "F-003", dt.date(2026, 10, 20), 30, 250000, 0),
            ("Cliente de ejemplo A", "F-004", dt.date(2026, 10, 1), 15, 120000, 120000),
            ("Cliente de ejemplo D", "F-005", dt.date(2026, 6, 15), 30, 80000, 0),
        ]
        for r, (cli, fac, em, plazo, val, ab) in enumerate(filas, 2):
            cc[f"A{r}"], cc[f"B{r}"], cc[f"C{r}"], cc[f"D{r}"], cc[f"F{r}"], cc[f"G{r}"] = cli, fac, em, plazo, val, ab
    wb.save(ruta)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tipo", choices=["gastos", "cartera"])
    p.add_argument("salida", help="archivo .xlsx a crear (si ya existe, no se pisa)")
    p.add_argument("--mes", help="gastos: mes fijo, formato AAAA-MM")
    p.add_argument("--corte", help="cartera: fecha de corte fija, formato AAAA-MM-DD")
    p.add_argument("--inventado", action="store_true", help="llenar con datos de mentira")
    a = p.parse_args(argv)
    try:
        import os
        if not a.salida.lower().endswith(".xlsx"):
            raise ValueError("el archivo de salida debe terminar en .xlsx")
        if os.path.exists(a.salida):
            raise ValueError(f"{a.salida} ya existe: no se pisa. Elige otro nombre.")
        if a.tipo == "gastos":
            mes = None
            if a.mes:
                y, m = a.mes.split("-")
                mes = (int(y), int(m))
                dt.date(mes[0], mes[1], 1)
            plantilla_gastos(a.salida, mes, a.inventado)
        else:
            corte = dt.date.fromisoformat(a.corte) if a.corte else None
            plantilla_cartera(a.salida, corte, a.inventado)
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(f"Creado {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
