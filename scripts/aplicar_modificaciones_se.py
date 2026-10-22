# -*- coding: utf-8 -*-
"""Aplica a data/reglas_se.json los Acuerdos SE que modifican las Reglas y criterios de
comercio exterior publicados en el DOF después del compilado SNICE (al 02-04-2026),
conservando el texto anterior en `historial` y registrando cada acuerdo en
data/modificaciones.json. Correr después de parse_se.py.

Los textos nuevos se leen de fuentes/reglas_se_mod_dof_AAAAMMDD.txt (el .doc del DOF
convertido con Word a texto). Cada cambio tiene un ancla; si no se encuentra, el script truena.
Los anexos del Acuerdo (tablas de fracciones) no se cargan en data/: sus cambios solo se registran.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
FUENTES = BASE / "fuentes"
COMPILADO = "Compilado SNICE al 02-04-2026"

AC_0528 = {
    "ordenamiento": "RCSE",
    "nombre": "Acuerdo que modifica el diverso por el que la SE emite Reglas y criterios de carácter general en materia de comercio exterior (permiso previo de importación de azúcar)",
    "dof": "28-05-2026",
    "en_vigor": "condicionada: cuando la DGFCCE comunique en el SNICE la liberación del trámite en la Ventanilla Digital (Transitorio Único)",
    "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5788843&fecha=28/05/2026",
    "fuente": "fuentes/reglas_se_mod_dof_20260528.txt",
    "reglas_afectadas": ["2.2.4", "2.2.19 BIS"],
    "anexos_afectados": ["2.2.1", "2.2.2"],
    "anexos_detalle": {"2.2.1": "numeral 8 TER adicionado (permiso previo: 1701.12.05, 1701.13.01, 1701.14.91, 1701.91.04, 1701.99.99, 1702.90.01 y 2106.90.99)",
                       "2.2.2": "numeral 8 adicionado"},
    "notas": ["Los anexos del Acuerdo SE no se cargan en data/; consultar el DOF.",
              "La clave C1 del apéndice 9 del Anexo 22 de las RGCE (2a RM) entra en vigor en términos de este Transitorio Único."],
}
AC_0529 = {
    "ordenamiento": "RCSE",
    "nombre": "Acuerdo que modifica el diverso por el que la SE emite Reglas y criterios de carácter general en materia de comercio exterior (PLATIICA; NOM-ENER-2025)",
    "dof": "29-05-2026",
    "en_vigor": "30-05-2026",
    "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5788992&fecha=29/05/2026",
    "fuente": "fuentes/reglas_se_mod_dof_20260529.txt",
    "reglas_afectadas": ["1.2.1", "2.4.3", "2.4.6", "2.4.11"],
    "anexos_afectados": ["2.4.1"],
    "anexos_detalle": {"2.4.1": "numerales 1 y 3 modificados; fracción 8413.60.01 eliminada del numeral 1 (resolutivo SEGUNDO)"},
    "notas": ["Los anexos del Acuerdo SE no se cargan en data/; consultar el DOF.",
              "Transitorio Segundo: los certificados vigentes de las NOM-004-ENER-2014, NOM-011-ENER-2006, NOM-014-ENER-2004 y NOM-016-ENER-2016 siguen sirviendo hasta el fin de su vigencia."],
}
AC_0928 = {
    "ordenamiento": "RCSE",
    "nombre": "Acuerdo que modifica el diverso por el que la SE emite reglas y criterios de carácter general en materia de comercio exterior (Anexo 2.4.1, numeral 1)",
    "dof": "28-09-2026",
    "en_vigor": "29-09-2026; lo relativo a la NOM-221-SCFI-2017 y NOM-221/2-SCFI-2018, a los 30 días hábiles siguientes a la publicación (Transitorio Único)",
    "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5799697&fecha=28/09/2026",
    "fuente": "fuentes/reglas_se_mod_dof_20260928.txt",
    "reglas_afectadas": [],
    "anexos_afectados": ["2.4.1"],
    "anexos_detalle": {"2.4.1": "numeral 1 modificado"},
    "notas": ["Solo modifica el Anexo 2.4.1, que no se carga en data/; no cambia ninguna regla. Consultar el DOF."],
}
ACUERDOS = (AC_0528, AC_0529, AC_0928)


def limpia(s):
    """Texto del .doc: sin sangrías ni tabuladores, espacios simples."""
    return re.sub(r"\s+", " ", s.replace("\t", " ")).strip()


def lee(ac):
    return [l for l in (BASE / ac["fuente"]).read_text(encoding="utf-8").splitlines()]


def idx(lineas, prefijo, desde=0):
    k = [i for i in range(desde, len(lineas)) if limpia(lineas[i]).startswith(prefijo)]
    assert k, f"ancla {prefijo!r} no encontrada"
    return k[0]


def unica(t, prefijo, etiqueta):
    k = [i for i, l in enumerate(t) if l.startswith(prefijo)]
    assert len(k) == 1, f"ancla {etiqueta!r}: {len(k)} coincidencias"
    return k[0]


def regla(d, num):
    return next(r for r in d["articulos"] if r["numero"] == num)


def guarda_historial(r, motivo, ac):
    previa = [h for h in r["historial"] if h.get("resolucion")]
    r["historial"].append({
        "vigente_hasta": ac["dof"],
        "fuente_anterior": ("Texto reformado por " + previa[-1]["resolucion"]) if previa else COMPILADO,
        "texto": r["texto"],
        "motivo": motivo,
        "resolucion": f"el Acuerdo SE, DOF {ac['dof']}",
    })
    r["notas_reforma"].append(motivo)


def aplicar_0528(d):
    ac = AC_0528
    L = lee(ac)
    cond = " (entrada en vigor condicionada a la liberación del trámite en la Ventanilla Digital, Transitorio Único)"

    # 2.2.4: se adiciona la fracción VI (con su párrafo)
    i = idx(L, "VI. En la DGFCCE")
    assert limpia(L[i + 2]) == "...", "2.2.4: fin de la fracción VI"
    r = regla(d, "2.2.4")
    t = r["texto"].split("\n")
    assert t[-2].startswith("V. En la DGFCCE") and not any(x.startswith("VI. ") for x in t), "ancla 2.2.4 fr. V"
    guarda_historial(r, f"Fracción VI adicionada, DOF {ac['dof']}" + cond, ac)
    r["texto"] = "\n".join(t + [limpia(L[i]), limpia(L[i + 1])])

    # 2.2.19 BIS: regla nueva, después de la 2.2.19
    ini = idx(L, "2.2.19 BIS Para efectos")
    fin = idx(L, "ANEXO 2.2.1", ini)
    cuerpo = [limpia(l) for l in L[ini:fin] if limpia(l)]
    assert cuerpo[-1].startswith("Las autorizaciones emitidas al amparo de la presente regla"), "2.2.19 BIS: último párrafo"
    assert not any(x["id"] == "RCSE-2.2.19-bis" for x in d["articulos"]), "2.2.19 BIS ya existe"
    base = regla(d, "2.2.19")
    nueva = {k: base[k] for k in ("titulo", "titulo_nombre", "capitulo", "capitulo_nombre", "seccion", "seccion_nombre")}
    nueva = {"id": "RCSE-2.2.19-bis", "numero": "2.2.19 BIS", "epigrafe": "", **nueva,
             "texto": "\n".join(cuerpo),
             "notas_reforma": [f"Regla adicionada, DOF {ac['dof']}" + cond],
             "historial": [], "referencias": []}
    pos = d["articulos"].index(base)
    d["articulos"].insert(pos + 1, nueva)


def aplicar_0529(d):
    ac = AC_0529
    L = lee(ac)

    # 1.2.1: se adiciona la fracción XLVI BIS (PLATIICA) y se deroga la LXXI (SINEC)
    platiica = limpia(L[idx(L, "XLVI BIS.")])
    assert limpia(L[idx(L, "LXXI.")]) == "LXXI. Se deroga."
    r = regla(d, "1.2.1")
    t = r["texto"].split("\n")
    k = unica(t, "XLVI.", "1.2.1 fr. XLVI")
    assert t[k + 1].startswith("Persona con discapacidad") and t[k + 2].startswith("XLVII. Programa IMMEX"), "ancla 1.2.1 XLVI/XLVII"
    k71 = unica(t, "LXXI.", "1.2.1 fr. LXXI")
    assert t[k71 + 1].startswith("SINEC, al portal electrónico"), "ancla 1.2.1 LXXI (SINEC)"
    guarda_historial(r, f"Fracción XLVI BIS adicionada y fracción LXXI derogada, DOF {ac['dof']}", ac)
    t[k71 + 1] = "Se deroga."
    t.insert(k + 2, platiica)
    r["texto"] = "\n".join(t)

    # 2.4.3: segundo párrafo
    i = idx(L, "2.4.3")
    nuevo = limpia(L[i + 1])
    assert nuevo.startswith("Los organismos de certificación acreditados al amparo") and "PLATIICA" in nuevo
    r = regla(d, "2.4.3")
    t = r["texto"].split("\n")
    k = unica(t, "Los organismos de certificación acreditados al amparo de un Acuerdo", "2.4.3 segundo párrafo")
    assert k == 1
    guarda_historial(r, f"Segundo párrafo reformado, DOF {ac['dof']}", ac)
    t[k] = nuevo
    r["texto"] = "\n".join(t)

    # 2.4.6: fracción I y párrafos segundo y tercero
    i = idx(L, "2.4.6")
    fr1 = limpia(L[i + 1])
    assert fr1.startswith("I. Transmitir") and limpia(L[i + 2]) == "II. ..."
    p2, p3 = limpia(L[i + 3]), limpia(L[i + 4])
    assert p2.startswith("La DGN publicará en la PLATIICA") and p3.startswith("Los laboratorios registrados")
    r = regla(d, "2.4.6")
    t = r["texto"].split("\n")
    a = unica(t, "I. Transmitir", "2.4.6 fr. I")
    b = unica(t, "II. Señalar", "2.4.6 fr. II")
    c = unica(t, "La DGN publicará", "2.4.6 segundo párrafo")
    assert b == a + 2 and c == b + 2 and len(t) == c + 3, f"2.4.6: estructura inesperada ({a},{b},{c},{len(t)})"
    guarda_historial(r, f"Fracción I y párrafos segundo y tercero reformados, DOF {ac['dof']}", ac)
    r["texto"] = "\n".join(t[:a] + [fr1] + t[b:c] + [p2, p3])

    # 2.4.11: fracción IX y segundo párrafo de la IX BIS
    i = idx(L, "IX. Las mercancías que se importen con pedimento")
    ix = [limpia(L[i]), limpia(L[i + 1])]
    assert ix[1].startswith("Para que proceda lo dispuesto en esta fracción el importador")
    j = idx(L, "IXBIS. ...", i)
    ixbis2 = limpia(L[j + 1])
    assert ixbis2.startswith("Para que proceda lo dispuesto en esta fracción se deberá anotar")
    r = regla(d, "2.4.11")
    t = r["texto"].split("\n")
    a = unica(t, "IX.", "2.4.11 fr. IX")
    b = unica(t, "IXBIS.", "2.4.11 fr. IX BIS")
    x = unica(t, "X.", "2.4.11 fr. X")
    assert t[a + 1].startswith("Las mercancías que se importen con pedimento") and b - a == 6, "ancla 2.4.11 fr. IX"
    assert t[b + 1].startswith("Para que proceda lo dispuesto en esta fracción se deberá anotar") and x - b == 4, "ancla 2.4.11 IX BIS"
    guarda_historial(r, f"Fracción IX y segundo párrafo de la fracción IX BIS reformados, DOF {ac['dof']}", ac)
    # en el compilado, las fracciones arancelarias que quedaron en renglones sueltos se reemplazan con el texto nuevo
    r["texto"] = "\n".join(t[:a] + ix + [t[b], ixbis2] + t[x:])


def main():
    d = json.loads((DATA / "reglas_se.json").read_text(encoding="utf-8"))
    aplicados = d.setdefault("acuerdos_aplicados", [])
    for ac, fn in ((AC_0528, aplicar_0528), (AC_0529, aplicar_0529), (AC_0928, None)):
        if ac["dof"] in aplicados:
            print(f"Acuerdo SE DOF {ac['dof']} ya estaba aplicado.")
            continue
        if fn:
            fn(d)
        aplicados.append(ac["dof"])
        d["modificaciones"].append(f"Modificación, DOF {ac['dof']}")
        print(f"Acuerdo SE DOF {ac['dof']} aplicado: reglas {', '.join(ac['reglas_afectadas']) or '(ninguna)'}; "
              f"anexos registrados: {', '.join(ac['anexos_afectados'])}.")
    d["ultima_reforma"] = ACUERDOS[-1]["dof"]
    d["total_articulos"] = len(d["articulos"])
    (DATA / "reglas_se.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    reg_path = DATA / "modificaciones.json"
    registro = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else []
    for ac in ACUERDOS:
        registro = [x for x in registro if x["nombre"] != ac["nombre"]] + [ac]
    reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Registro de resoluciones:", len(registro), "entrada(s) en modificaciones.json")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
