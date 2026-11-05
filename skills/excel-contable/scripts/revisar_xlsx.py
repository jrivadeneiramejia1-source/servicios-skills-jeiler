#!/usr/bin/env python3
"""Revisa un Excel y cuenta sus problemas SIN mostrar su contenido.

  python3 revisar_xlsx.py archivo.xlsx [--recalcular] [--json] [--mostrar-encabezados]

Pensado para archivos de clientes: el informe solo trae cantidades y coordenadas de celdas (por ejemplo «C14»),
nunca valores ni nombres de personas. Se puede compartir con quien te ayuda (o con una IA) sin pasar los datos.
El archivo original NO se modifica. Con --recalcular se calcula una copia temporal con LibreOffice (sin internet)
para encontrar errores de fórmulas; sin eso, solo se ven los errores que Excel ya dejó guardados.
Requiere: pip install openpyxl   (y LibreOffice solo para --recalcular)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

from openpyxl import load_workbook

ERRORES = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!"}
VOLATILES = ("TODAY(", "NOW(", "INDIRECT(", "OFFSET(", "RAND(", "RANDBETWEEN(")
RE_NUM_TEXTO = re.compile(r"^\s*[-+]?\$?\s*\d[\d.,]*\s*%?\s*$")
RE_FECHA_TEXTO = re.compile(r"^\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\s*$")
MAX_COORDS = 10


def coords(lista):
    return lista[:MAX_COORDS] + ([f"y {len(lista) - MAX_COORDS} más"] if len(lista) > MAX_COORDS else [])


def recalcular(ruta):
    """Devuelve (carpeta_temporal, ruta_recalculada). Trabaja sobre una copia."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise RuntimeError("No encontré LibreOffice (soffice). Instálalo o corre sin --recalcular.")
    tmp = tempfile.mkdtemp(prefix="revisar-xlsx-")
    entrada = os.path.join(tmp, "entrada")
    salida = os.path.join(tmp, "salida")
    os.makedirs(entrada)
    os.makedirs(salida)
    copia = os.path.join(entrada, "copia.xlsx")
    shutil.copyfile(ruta, copia)
    try:
        subprocess.run(
            [soffice, f"-env:UserInstallation=file://{tmp}/perfil", "--headless", "--convert-to", "xlsx", "--outdir", salida, copia],
            check=True, capture_output=True, timeout=180,
        )
    except (subprocess.SubprocessError, OSError) as e:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f"LibreOffice no pudo recalcular: {type(e).__name__}")
    return tmp, os.path.join(salida, "copia.xlsx")


def revisar(ruta, con_recalculo=False, mostrar_encabezados=False):
    if not os.path.isfile(ruta):
        raise ValueError("No encuentro el archivo.")
    if not ruta.lower().endswith((".xlsx", ".xlsm")):
        raise ValueError("Solo se revisan archivos .xlsx o .xlsm (guarda el .xls como .xlsx).")
    try:
        wb_f = load_workbook(ruta, data_only=False)
    except Exception as e:  # archivo dañado o protegido
        raise ValueError(f"No se pudo abrir el archivo ({type(e).__name__}). ¿Está dañado o tiene clave?")
    tmp = None
    ruta_valores = ruta
    if con_recalculo:
        tmp, ruta_valores = recalcular(ruta)
    try:
        wb_v = load_workbook(ruta_valores, data_only=True)
    finally:
        pass
    informe = {"hojas": [], "libro": {"hojas_ocultas": 0, "vinculos_externos": len(getattr(wb_f, "_external_links", []))}, "recalculado": bool(con_recalculo)}
    for ws in wb_f.worksheets:
        wv = wb_v[ws.title] if ws.title in wb_v.sheetnames else None
        h = {"hoja": f"hoja {len(informe['hojas']) + 1}", "oculta": ws.sheet_state != "visible", "protegida": bool(ws.protection.sheet),
             "filas": ws.max_row, "columnas": ws.max_column, "celdas_combinadas": len(ws.merged_cells.ranges),
             "validaciones": sum(len(dv.sqref.ranges) for dv in ws.data_validations.dataValidation),
             "filas_ocultas": sum(1 for d in ws.row_dimensions.values() if d.hidden),
             "columnas_ocultas": sum(1 for d in ws.column_dimensions.values() if d.hidden)}
        if h["oculta"]:
            informe["libro"]["hojas_ocultas"] += 1
        formulas, volatiles = 0, Counter()
        errores, sin_valor, numeros_a_mano, num_texto, fecha_texto = [], 0, [], [], []
        por_columna = {}
        for fila in ws.iter_rows():
            for c in fila:
                if c.value is None:
                    continue
                por_columna.setdefault(c.column, []).append(c)
        for col, celdas in por_columna.items():
            datos = [c for c in celdas if c.row > 1]
            es_formula = [c for c in datos if isinstance(c.value, str) and c.value.startswith("=")]
            numericas = [c for c in datos if isinstance(c.value, (int, float)) and not isinstance(c.value, bool)]
            fechas = [c for c in datos if hasattr(c.value, "year")]
            textos = [c for c in datos if isinstance(c.value, str) and not c.value.startswith("=")]
            formulas += len(es_formula)
            for c in es_formula:
                up = c.value.upper()
                for v in VOLATILES:
                    if v in up:
                        volatiles[v[:-1]] += 1
                if wv is not None:
                    val = wv.cell(c.row, c.column).value
                    if isinstance(val, str) and val in ERRORES:
                        errores.append(c.coordinate)
                    elif val is None and not con_recalculo:
                        sin_valor += 1
            if len(datos) >= 4 and len(es_formula) / len(datos) >= 0.6:
                numeros_a_mano += [c.coordinate for c in numericas]
            if len(numericas) >= 3 and len(numericas) >= len(textos):
                num_texto += [c.coordinate for c in textos if RE_NUM_TEXTO.match(c.value)]
            if len(fechas) >= 3 and len(fechas) >= len(textos):
                fecha_texto += [c.coordinate for c in textos if RE_FECHA_TEXTO.match(c.value)]
        # errores guardados en celdas que no son fórmulas (valores pegados)
        if wv is not None:
            for fila in wv.iter_rows():
                for c in fila:
                    if isinstance(c.value, str) and c.value in ERRORES and c.coordinate not in errores:
                        errores.append(c.coordinate)
        h.update({"formulas": formulas, "funciones_volatiles": dict(volatiles), "celdas_con_error": len(errores), "coordenadas_error": coords(sorted(errores)),
                  "formulas_sin_valor_guardado": sin_valor,
                  "numeros_escritos_a_mano_en_columna_de_formulas": len(numeros_a_mano), "coordenadas_numeros_a_mano": coords(numeros_a_mano),
                  "numeros_guardados_como_texto": len(num_texto), "coordenadas_numeros_texto": coords(num_texto),
                  "fechas_guardadas_como_texto": len(fecha_texto), "coordenadas_fechas_texto": coords(fecha_texto)})
        encabezados = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        vistos = [str(x).strip().lower() for x in encabezados if isinstance(x, str) and x.strip()]
        h["encabezados_repetidos"] = sum(1 for _, n in Counter(vistos).items() if n > 1)
        # Solo se exige encabezado en hojas que parecen tabla (2 o más textos en la fila 1); un resumen no es una tabla.
        h["encabezados_vacios_en_columnas_con_datos"] = (
            sum(1 for col, cel in por_columna.items() if ws.cell(1, col).value in (None, "") and any(c.row > 1 for c in cel)) if len(vistos) >= 2 else 0
        )
        if mostrar_encabezados:
            h["encabezados"] = [str(x) for x in encabezados if x is not None]
        informe["hojas"].append(h)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    return informe


def a_texto(inf):
    L = []
    L.append(f"Hojas: {len(inf['hojas'])} (ocultas: {inf['libro']['hojas_ocultas']}) · vínculos a otros archivos: {inf['libro']['vinculos_externos']} · recalculado: {'sí' if inf['recalculado'] else 'no'}")
    avisos = 0
    for h in inf["hojas"]:
        L.append(f"\n[{h['hoja']}] {h['filas']} filas × {h['columnas']} columnas · fórmulas: {h['formulas']}" + (" · OCULTA" if h["oculta"] else "") + (" · protegida" if h["protegida"] else ""))

        def linea(texto, n, cs=None):
            nonlocal avisos
            if n:
                avisos += 1
                L.append(f"  ⚠ {texto}: {n}" + (f" → {', '.join(cs)}" if cs else ""))
        linea("celdas con error de fórmula (#REF!, #DIV/0!...)", h["celdas_con_error"], h["coordenadas_error"])
        linea("fórmulas sin valor guardado (usa --recalcular)", h["formulas_sin_valor_guardado"])
        linea("números escritos a mano en una columna de fórmulas", h["numeros_escritos_a_mano_en_columna_de_formulas"], h["coordenadas_numeros_a_mano"])
        linea("números guardados como texto (no suman)", h["numeros_guardados_como_texto"], h["coordenadas_numeros_texto"])
        linea("fechas guardadas como texto (no ordenan ni restan)", h["fechas_guardadas_como_texto"], h["coordenadas_fechas_texto"])
        linea("celdas combinadas (estorban a los filtros y tablas)", h["celdas_combinadas"])
        linea("encabezados repetidos", h["encabezados_repetidos"])
        linea("columnas con datos y sin encabezado", h["encabezados_vacios_en_columnas_con_datos"])
        linea("filas ocultas", h["filas_ocultas"])
        linea("columnas ocultas", h["columnas_ocultas"])
        if h["funciones_volatiles"]:
            L.append(f"  ℹ funciones que cambian solas al abrir: {', '.join(f'{k} ×{v}' for k, v in h['funciones_volatiles'].items())}")
        L.append(f"  ℹ listas desplegables y validaciones: {h['validaciones']}")
        if "encabezados" in h:
            L.append(f"  ℹ encabezados: {', '.join(h['encabezados'])}")
    if inf["libro"]["hojas_ocultas"]:
        avisos += 1
        L.append(f"\n⚠ hojas ocultas: {inf['libro']['hojas_ocultas']}")
    if inf["libro"]["vinculos_externos"]:
        avisos += 1
        L.append(f"⚠ el libro depende de {inf['libro']['vinculos_externos']} archivo(s) externo(s)")
    L.append(f"\nAvisos: {avisos}. Este informe no incluye valores ni nombres de personas; solo cantidades y coordenadas.")
    return "\n".join(L)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("archivo")
    p.add_argument("--recalcular", action="store_true", help="calcular una copia con LibreOffice para encontrar errores")
    p.add_argument("--json", action="store_true", help="salida en JSON")
    p.add_argument("--mostrar-encabezados", action="store_true", help="incluir los nombres de las columnas (revísalos: pueden ser sensibles)")
    a = p.parse_args(argv)
    try:
        inf = revisar(a.archivo, a.recalcular, a.mostrar_encabezados)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(inf, ensure_ascii=False, indent=1) if a.json else a_texto(inf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
