#!/usr/bin/env python3
"""Cotizador en pesos colombianos (COP) para los servicios de Jeiler.

Dos usos:
  python cotizar.py cotizacion.json [--md salida.md]
  python cotizar.py tarifa --ingreso 1500000 --costos 200000 --horas 60

El script NO trae precios ni horas de mercado: todo lo escribe quien lo usa y
queda marcado como supuesto en el resultado. Solo usa la librería estándar.
"""
import argparse
import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_CEILING

COLCHON_POR_DEFECTO = Decimal("0.25")
REDONDEO_POR_DEFECTO = Decimal("1000")


class ErrorDeDatos(ValueError):
    """Dato mal escrito en el archivo; el mensaje se muestra tal cual."""


def numero(valor, nombre, minimo=None, maximo=None, estricto_mayor=False):
    if isinstance(valor, bool):
        raise ErrorDeDatos(f"«{nombre}» debe ser un número, no sí/no.")
    try:
        d = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ErrorDeDatos(f"«{nombre}» debe ser un número (llegó: {valor!r}).")
    if not d.is_finite():
        raise ErrorDeDatos(f"«{nombre}» no es un número válido.")
    if minimo is not None and (d <= minimo if estricto_mayor else d < minimo):
        raise ErrorDeDatos(f"«{nombre}» debe ser {'mayor que' if estricto_mayor else 'al menos'} {minimo}.")
    if maximo is not None and d > maximo:
        raise ErrorDeDatos(f"«{nombre}» no puede pasar de {maximo}.")
    return d


def subir(valor, paso):
    """Redondea hacia arriba al múltiplo de `paso` (nunca cobrar de menos por redondeo)."""
    return (valor / paso).to_integral_value(rounding=ROUND_CEILING) * paso


def pesos(n):
    return "$" + f"{int(n):,}".replace(",", ".")


def tarifa_hora(ingreso_mensual, costos_mensuales, horas_facturables):
    """Tarifa mínima por hora para llegar al ingreso deseado.

    horas_facturables = horas al mes que de verdad se pueden cobrar (sin contar
    buscar clientes, cobrar, aprender ni los imprevistos).
    """
    ingreso = numero(ingreso_mensual, "ingreso", 0)
    costos = numero(costos_mensuales, "costos", 0)
    horas = numero(horas_facturables, "horas", 0, estricto_mayor=True)
    return subir((ingreso + costos) / horas, REDONDEO_POR_DEFECTO)


def calcular(datos):
    if not isinstance(datos, dict):
        raise ErrorDeDatos("El archivo debe ser un objeto JSON con los campos de la cotización.")
    tarifa = numero(datos.get("tarifa_hora"), "tarifa_hora", 0, estricto_mayor=True)
    colchon = numero(datos.get("colchon", COLCHON_POR_DEFECTO), "colchon", 0, Decimal("2"))
    paso = numero(datos.get("redondeo", REDONDEO_POR_DEFECTO), "redondeo", 1)
    descuento = numero(datos.get("descuento_pct", 0), "descuento_pct", 0, Decimal("100"))

    tareas = datos.get("tareas")
    if not isinstance(tareas, list) or not tareas:
        raise ErrorDeDatos("Falta la lista «tareas» (cada una con nombre y horas).")
    filas = []
    for i, t in enumerate(tareas, 1):
        if not isinstance(t, dict) or not str(t.get("nombre", "")).strip():
            raise ErrorDeDatos(f"La tarea {i} necesita un «nombre».")
        filas.append({"nombre": str(t["nombre"]).strip(), "horas": numero(t.get("horas"), f"horas de la tarea {i}", 0, estricto_mayor=True)})
    horas_base = sum(f["horas"] for f in filas)
    horas_con_colchon = horas_base * (1 + colchon)
    valor_trabajo = subir(horas_con_colchon * tarifa, paso)
    valor_descuento = subir(valor_trabajo * descuento / 100, paso) if descuento else Decimal(0)
    valor_descuento = min(valor_descuento, valor_trabajo)
    a_pagar = valor_trabajo - valor_descuento

    externos = []
    for i, c in enumerate(datos.get("costos_externos", []) or [], 1):
        if not isinstance(c, dict) or not str(c.get("nombre", "")).strip():
            raise ErrorDeDatos(f"El costo externo {i} necesita un «nombre».")
        paga = c.get("paga", "cliente")
        periodo = c.get("periodo", "unico")
        if paga not in ("cliente", "jeiler"):
            raise ErrorDeDatos(f"El costo externo «{c['nombre']}»: «paga» debe ser cliente o jeiler.")
        if periodo not in ("unico", "mensual"):
            raise ErrorDeDatos(f"El costo externo «{c['nombre']}»: «periodo» debe ser unico o mensual.")
        externos.append({"nombre": str(c["nombre"]).strip(), "cop": numero(c.get("cop"), f"cop de «{c['nombre']}»", 0), "paga": paga, "periodo": periodo})

    mantenimiento = None
    m = datos.get("mantenimiento_mensual")
    if m:
        horas_m = numero(m.get("horas_mes"), "horas_mes", 0, estricto_mayor=True)
        mantenimiento = {"descripcion": str(m.get("descripcion", "Mantenimiento")).strip(), "horas": horas_m, "cop": subir(horas_m * tarifa, paso)}

    return {
        "cliente": str(datos.get("cliente", "(sin alias)")).strip(),
        "servicio": str(datos.get("servicio", "(sin nombre)")).strip(),
        "tarifa": tarifa, "colchon": colchon, "paso": paso,
        "tareas": filas, "horas_base": horas_base, "horas_con_colchon": horas_con_colchon,
        "valor_trabajo": valor_trabajo, "descuento_pct": descuento, "descuento_motivo": str(datos.get("descuento_motivo", "")).strip(),
        "valor_descuento": valor_descuento, "a_pagar": a_pagar,
        "externos": externos, "mantenimiento": mantenimiento,
        "nota": str(datos.get("nota", "")).strip(),
    }


def horas(d):
    return f"{d.normalize():f}".rstrip("0").rstrip(".") if d % 1 else f"{int(d)}"


def a_markdown(r):
    L = [f"# Cotización: {r['servicio']}", f"Cliente: {r['cliente']}", ""]
    L += ["| Tarea | Horas |", "|---|---:|"]
    L += [f"| {t['nombre']} | {horas(t['horas'])} |" for t in r["tareas"]]
    L += ["", f"- Horas estimadas: {horas(r['horas_base'])}",
          f"- Colchón por imprevistos ({int(r['colchon'] * 100)} %): {horas(r['horas_con_colchon'])} horas en total",
          f"- Tarifa por hora: {pesos(r['tarifa'])}",
          f"- **Valor del trabajo: {pesos(r['valor_trabajo'])}**"]
    if r["valor_descuento"]:
        motivo = f" ({r['descuento_motivo']})" if r["descuento_motivo"] else ""
        L.append(f"- Descuento {horas(r['descuento_pct'])} %{motivo}: -{pesos(r['valor_descuento'])}")
    L.append(f"- **A pagar por el trabajo: {pesos(r['a_pagar'])}**")
    if r["externos"]:
        L += ["", "## Costos de terceros (no son ganancia de Jeiler)", "| Concepto | Valor | Lo paga | Cuándo |", "|---|---:|---|---|"]
        L += [f"| {c['nombre']} | {pesos(c['cop'])} | {c['paga']} | {'cada mes' if c['periodo'] == 'mensual' else 'una vez'} |" for c in r["externos"]]
    if r["mantenimiento"]:
        m = r["mantenimiento"]
        L += ["", f"## Mantenimiento mensual (opcional)\n{m['descripcion']}: {horas(m['horas'])} h al mes = {pesos(m['cop'])} al mes"]
    L += ["", "## Supuestos (revisar antes de enviar al cliente)",
          "- La tarifa por hora, las horas de cada tarea y el colchón son **estimaciones de Jeiler, no precios de mercado**.",
          "- Si el cliente pide algo fuera de la lista de tareas, se cotiza aparte (ver el alcance firmado).",
          "- Los costos de terceros (Cloudflare, Meta, dominios, etc.) cambian: confirmar su valor vigente el día de cotizar.",
          "- Los impuestos y la factura dependen de cómo esté registrado Jeiler: consultarlo con un contador."]
    if r["nota"]:
        L += ["", f"Nota: {r['nota']}"]
    return "\n".join(L) + "\n"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] == ["tarifa"]:
            t = argparse.ArgumentParser(prog="cotizar.py tarifa", description="Calcular la tarifa mínima por hora")
            t.add_argument("--ingreso", required=True, help="pesos que quieres ganar al mes")
            t.add_argument("--costos", default="0", help="gastos del mes (internet, luz, herramientas), en pesos")
            t.add_argument("--horas", required=True, help="horas facturables al mes (sin contar buscar clientes ni imprevistos)")
            a = t.parse_args(argv[1:])
            v = tarifa_hora(a.ingreso, a.costos, a.horas)
            print(f"Tarifa mínima por hora: {pesos(v)}\n(Es una cuenta, no un precio de mercado: compárala con lo que cobran otros en tu zona antes de usarla.)")
            return 0
        p = argparse.ArgumentParser(prog="cotizar.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        p.add_argument("archivo", help="cotizacion.json")
        p.add_argument("--md", help="guardar el resultado en este archivo .md")
        a = p.parse_args(argv)
        with open(a.archivo, encoding="utf-8") as f:
            datos = json.load(f)
        md = a_markdown(calcular(datos))
    except (ErrorDeDatos, OSError, json.JSONDecodeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Guardado en {a.md}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
