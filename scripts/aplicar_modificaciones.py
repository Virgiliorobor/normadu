# -*- coding: utf-8 -*-
"""Aplica a data/rgce.json las resoluciones de modificaciones publicadas en el DOF,
conservando el texto anterior en `historial` y registrando cada resolución en
data/modificaciones.json.

Cada modificación se codifica como parches explícitos con anclas de texto; si un
ancla no se encuentra, el script truena para no aplicar cambios a ciegas.
"""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

RM1 = {
    "ordenamiento": "RGCE",
    "nombre": "Primera Resolución de Modificaciones a las RGCE para 2026 y Anexos 5, 22 y 29",
    "dof": "14-05-2026",
    "dof_anexos": "20-05-2026",
    "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5787425&fecha=14/05/2026",
    "reglas_afectadas": ["1.4.14", "1.5.1", "4.8.2", "4.8.4", "Transitorio Décimo Primero"],
    "anexos_afectados": ["5", "22", "29"],
}

NUEVO_1_4_14 = """1.4.14. Para los efectos del artículo 162, fracción VI de la Ley, el agente aduanal deberá integrar un expediente electrónico con la información proporcionada por cada usuario que solicite operaciones de comercio exterior, mismo que contará con la siguiente información y documentación:
I.\tIdentificación oficial, tratándose de personas físicas.
II.\tActa constitutiva o instrumento notarial y sus modificaciones, e identificación oficial del representante legal, tratándose de personas morales.
III.\tDatos de contacto: correo electrónico y números telefónicos.
IV.\tComprobante del domicilio en donde realiza las actividades relacionadas con la operación de comercio exterior.
V.\tClave en el RFC o número de identificación fiscal, o su equivalente, en caso de ser residente en el extranjero, para efectos fiscales.
VI.\tConstancia de situación fiscal a que se refiere la regla 2.4.9. de la RMF, en su caso.
VII.\tManifestación bajo protesta de decir verdad del usuario que solicitó la operación, señalando:
a)\tDescripción o características del inmueble en el que realiza las actividades relacionadas con la operación de comercio exterior, así como de la maquinaria, equipo de oficina, medios de transporte y demás medios empleados para la realización de sus actividades, debiendo incluir fotografías de cada bien descrito.
\tEn la manifestación a que se refiere el párrafo anterior, el usuario deberá señalar que cuenta con la documentación con la que acredita la legal propiedad o posesión de los bienes descritos.
b)\tQue no tiene vinculación, en términos del artículo 68 de la Ley con contribuyentes que se encuentren en el listado a que se refiere el artículo 69-B, cuarto párrafo del CFF.
c)\tQue no se le ha emitido y notificado la resolución que determine que emite falsos comprobantes fiscales, en términos del artículo 49 Bis del CFF.
VIII.\tManifestación bajo protesta de decir verdad en la que el agente aduanal señale que verificó que el usuario no se encuentra publicado en el listado a que se refieren los artículos 49 Bis, fracción X, 69, con excepción de la fracción VI, 69-B, cuarto párrafo o 69-B Bis del CFF.
\tEl expediente electrónico a que se refiere esta regla se integrará con la información proporcionada por cada usuario y deberá actualizarse cada tres años, o bien, cuando el usuario informe al agente aduanal que la información proporcionada ha sido modificada."""
CORREL_1_4_14 = "Ley 68, 162, CFF 49 Bis, 69, 69-B, 69-B Bis, RMF 2.4.9."

NUEVO_INCISO_D = "d)\tSe trate de las importaciones temporales señaladas en el artículo 106, fracciones II, incisos a), c) y d), III o IV, inciso b) de la Ley."
NUEVO_INCISO_E = "e)\tSe trate del pedimento global complementario, a que se refiere la regla 6.2.1."
NUEVO_PARRAFO_1_5_1 = ("En aquellas operaciones en las que la introducción se efectúe mediante documento aduanero "
    "distinto del pedimento o en las que no sea necesario hacer la transmisión a que se refieren las reglas 1.9.16. "
    "y 1.9.17., la información y documentación correspondiente al valor de la mercancía declarado deberá entregarse "
    "a requerimiento de la autoridad aduanera, en términos del artículo 59, fracción III, primer párrafo de la Ley.")
CORREL_1_5_1 = ("Ley 59, 59-A, 59-B, 64, 103, 106, 116, 162, 185, CFF 30, Reglamento 68, 81, 220, "
                "RGCE 1.9.16., 1.9.17., 4.5.30., 6.1.1., 6.2.1., Anexo 1")

NUEVO_PARRAFO_4_8_4 = ("Lo dispuesto en el Anexo 29, fracción III no será aplicable tratándose de mercancías que se "
    "destinen al régimen de recinto fiscalizado estratégico por empresas que cuenten con autorización para el PROSEC "
    "de la Industria Automotriz y de Autopartes.")
CORREL_4_8_4 = "Ley 90, 135-B, RGCE Anexo 29"

NUEVO_TRANS_11 = ("Décimo\nPrimero.\tPara los efectos del artículo 59, fracción III de la Ley y de la regla 1.5.1., "
    "hasta el 31 de mayo de 2026, quienes introduzcan mercancías a territorio nacional podrán cumplir con las "
    "referidas disposiciones, en términos de lo establecido en el Transitorio Quinto, segundo párrafo de las RGCE "
    "para 2025, publicadas en el DOF el 30 de diciembre de 2024.")

NOTA = "Regla reformada por la 1a Resolución de Modificaciones a las RGCE para 2026, DOF 14-05-2026"

ORIGINAL = "RGCE 2026 original, DOF 27-12-2025"


def regla(d, num):
    return next(r for r in d["articulos"] if r["numero"] == num)


def fuente_vigente(r):
    """Texto del que proviene la versión vigente de una entrada (para `fuente_anterior`)."""
    if not r["historial"]:
        for pref, fuente in (("RGCE-anexo-1", "Anexo 1 original, DOF 08-01-2026"), ("RGCE-anexo-2-", "Anexo 2 original, DOF 12-01-2026"),
                             ("RGCE-anexo-2", "Anexo 2 original, DOF 12-01-2026"), ("RGCE-anexo-22", "Anexo 22 original, DOF 15-01-2026")):
            if r["id"] == pref or r["id"].startswith(pref + "-") or pref.endswith("-") and r["id"].startswith(pref):
                return fuente
        return ORIGINAL
    return "Texto reformado por " + r["historial"][-1].get("resolucion", "la 1a RM RGCE 2026, DOF 14-05-2026")


def guarda_historial(r, motivo, vigente_hasta="14-05-2026", resolucion=None):
    h = {
        "vigente_hasta": vigente_hasta,
        "fuente_anterior": fuente_vigente(r),
        "texto": r["texto"],
        "correlaciones": r.get("correlaciones", ""),
        "motivo": motivo,
    }
    if resolucion:
        h["epigrafe"] = r.get("epigrafe", "")
        h["resolucion"] = resolucion
    r["historial"].append(h)
    if resolucion or NOTA not in r["notas_reforma"]:
        r["notas_reforma"].append(motivo)


def parse_correl(texto):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_rgce import parse_correlaciones
    return parse_correlaciones(texto)


def aplicar_rm1(d):
    # --- 1.4.14: reforma íntegra
    r = regla(d, "1.4.14")
    guarda_historial(r, NOTA)
    r["texto"] = NUEVO_1_4_14
    r["correlaciones"] = CORREL_1_4_14
    r["referencias"] = parse_correl(CORREL_1_4_14)

    # --- 1.5.1: reforma inciso d), adiciona e) y segundo párrafo de la fracc. VII
    r = regla(d, "1.5.1")
    guarda_historial(r, "Fracción VII, inciso d) reformado; inciso e) y párrafo adicionados por la 1a RM RGCE 2026, DOF 14-05-2026")
    lineas = r["texto"].split("\n")
    idx_d = next(i for i, l in enumerate(lineas) if l.startswith("d)"))
    assert "importaciones temporales" in lineas[idx_d], "ancla inciso d) de 1.5.1 no encontrada"
    lineas[idx_d] = NUEVO_INCISO_D
    lineas.insert(idx_d + 1, NUEVO_INCISO_E)
    lineas.insert(idx_d + 2, NUEVO_PARRAFO_1_5_1)
    r["texto"] = "\n".join(lineas)
    r["correlaciones"] = CORREL_1_5_1
    r["referencias"] = parse_correl(CORREL_1_5_1)

    # --- 4.8.2: se deroga el segundo párrafo
    r = regla(d, "4.8.2")
    guarda_historial(r, "Segundo párrafo derogado por la 1a RM RGCE 2026, DOF 14-05-2026 (vigente a partir de la publicación de la modificación del Anexo 29, DOF 20-05-2026)")
    lineas = r["texto"].split("\n")
    assert len(lineas) >= 2 and lineas[1].startswith("Asimismo"), "ancla segundo párrafo de 4.8.2 no encontrada"
    lineas[1] = "(Se deroga el segundo párrafo — 1a RM RGCE 2026, DOF 14-05-2026)"
    r["texto"] = "\n".join(lineas)

    # --- 4.8.4: se adiciona segundo párrafo
    r = regla(d, "4.8.4")
    guarda_historial(r, "Segundo párrafo adicionado por la 1a RM RGCE 2026, DOF 14-05-2026 (vigente a partir de la publicación de la modificación del Anexo 29, DOF 20-05-2026)")
    r["texto"] = r["texto"].rstrip() + "\n" + NUEVO_PARRAFO_4_8_4
    r["correlaciones"] = CORREL_4_8_4
    r["referencias"] = parse_correl(CORREL_4_8_4)

    # --- Anexo 22, Apéndice 9: se adiciona la clave AL (SE) antes de AV
    r = next(x for x in d["articulos"] if x["id"] == "RGCE-anexo-22-ap9")
    guarda_historial(r, "Clave AL adicionada al Apéndice 9 (Secretaría de Economía) por la Primera Modificación al Anexo 22, 1a RM RGCE 2026, DOF 20-05-2026")
    lineas = r["texto"].split("\n")
    idx_av = next(i for i in range(len(lineas) - 1)
                  if lineas[i].strip() == "AV" and lineas[i + 1].startswith("Aviso automático de la SE"))
    lineas[idx_av:idx_av] = ["AL", "Aviso automático de importación de aluminio."]
    r["texto"] = "\n".join(lineas)

    # --- Transitorio Décimo Primero: reforma
    reforma_transitorio(d, "Décimo\nPrimero", NUEVO_TRANS_11, "14-05-2026", ORIGINAL,
                        "Transitorio Décimo Primero reformado por la 1a RM RGCE 2026, DOF 14-05-2026")

    d["ultima_reforma"] = RM1["dof"]
    print("1a RM RGCE 2026 aplicada: reglas 1.4.14, 1.5.1, 4.8.2, 4.8.4 y Transitorio Décimo Primero.")


def reforma_transitorio(d, nombre, nuevo, vigente_hasta, fuente_anterior, motivo):
    """Sustituye un transitorio en d["transitorios"] y guarda el texto anterior en
    d["transitorios_historial"]."""
    m = re.search(nombre + r"\.\t.*?(?=\n(?:Décimo|Vigésimo|Primero|Segundo|Tercero|Cuarto|Quinto|Sexto|Séptimo|Octavo|Noveno)\b[^\n]*\n?[^\n]*\.\t)",
                  d["transitorios"], re.S)
    assert m, f"ancla Transitorio {nombre!r} no encontrada"
    d.setdefault("transitorios_historial", []).append({
        "transitorio": nombre.replace("\n", " "), "vigente_hasta": vigente_hasta,
        "fuente_anterior": fuente_anterior, "texto": m.group(0), "motivo": motivo,
    })
    d["transitorios"] = d["transitorios"][:m.start()] + nuevo + d["transitorios"][m.end():]


# ---------------------------------------------------------------------------
# 2a Resolución de Modificaciones a las RGCE para 2026 y anexos 1, 2 y 22
# (DOF 22-09-2026; en vigor el 23-09-2026). Los textos nuevos se toman de las
# fuentes descargadas, con anclas; si un ancla falla, el script truena.

FUENTES = DATA.parent / "fuentes"
RM2_DOC = FUENTES / "rgce2026_2rm_anexos_1_2_22_dof_20260922_celdas.txt"   # .doc DOF -> txt (una celda por línea)
RM2_ANEXO1 = FUENTES / "rgce2026_2rm_anexo1_mod1_dof_20260922_layout.txt"  # PDF SAT, pdftotext -layout
RM2_ANEXO2 = FUENTES / "rgce2026_2rm_anexo2_mod1_dof_20260922.txt"         # PDF SAT, pdftotext

RM2 = {
    "ordenamiento": "RGCE",
    "nombre": "Segunda Resolución de Modificaciones a las RGCE para 2026 y anexos 1, 2 y 22",
    "dof": "22-09-2026",
    "en_vigor": "23-09-2026",
    "url": "https://www.dof.gob.mx/nota_detalle.php?codigo=5799243&fecha=22/09/2026",
    "glosario": ["fracción III, numeral 40"],
    "reglas_afectadas": ["1.4.12", "1.4.14", "3.1.2", "3.7.20", "4.5.15", "4.5.33", "4.6.11",
                         "7.1.4", "7.1.5", "7.2.1", "Transitorio Décimo Primero"],
    "anexos_afectados": ["1", "2", "22"],
    "anexos_detalle": {
        "1": "Primera Modificación: Contenido (E15 adicionado; F1 y F3), apartado I, inciso a), numeral 3 derogado; formato E15 adicionado; formatos F1 y F3 reformados",
        "2": "Primera Modificación: apartado I, inciso a), numeral 3 derogado; 37 fichas reformadas",
        "22": "Segunda Modificación: apéndices 6 y 13 sustituidos; apéndice 8 (AO adicionado; EX y GA reformados); apéndice 9 (C1 de la SE reformado)",
    },
    "notas": ["La modificación a la clave C1 del apéndice 9 del Anexo 22 entra en vigor en términos del Transitorio Único del "
              "Acuerdo SE publicado en el DOF el 28-05-2026 (Transitorio Segundo de la 2a RM)."],
}
VIG2 = "22-09-2026"
RES2 = "la 2a RM RGCE 2026, DOF 22-09-2026"
MOT2 = "reforma de la 2a Resolución de Modificaciones a las RGCE para 2026, DOF 22-09-2026 (en vigor el 23-09-2026)"


def lee_rm2():
    lineas = RM2_DOC.read_text(encoding="utf-8").splitlines()
    fin = next(i for i, l in enumerate(lineas) if l.strip().startswith("SEGUNDO. Se reforma el Transitorio"))
    return lineas, fin


CORREL_RE = re.compile(r'^\t?Ley \d')


def bloque_rm2(lineas, fin, num):
    """Líneas publicadas para la regla `num` (sin epígrafe) y su línea de correlaciones."""
    ini = next(i for i, l in enumerate(lineas[:fin]) if l.startswith(num + ".\t"))
    epigrafe = lineas[ini - 1].strip()
    cuerpo = []
    for l in lineas[ini:fin]:
        if CORREL_RE.match(l):
            return epigrafe, cuerpo, l.strip().rstrip('"').strip()
        cuerpo.append(l)
    raise AssertionError(f"sin correlaciones para {num}")


def primera(num, linea):
    """La primera línea del .doc trae 'n.n.n.\\t'; en rgce.json va 'n.n.n. '."""
    return linea.replace(num + ".\t", num + ". ", 1)


def sustituye_linea(lineas, prefijo, nueva, etiqueta):
    idx = [i for i, l in enumerate(lineas) if l.startswith(prefijo)]
    assert len(idx) == 1, f"ancla {etiqueta!r}: {len(idx)} coincidencias"
    lineas[idx[0]] = nueva


def aplicar_rm2_reglas(d):
    lineas, fin = lee_rm2()

    def prepara(num, motivo):
        r = regla(d, num)
        epi, cuerpo, correl = bloque_rm2(lineas, fin, num)
        guarda_historial(r, f"Regla {num}: {motivo}", VIG2, RES2)
        if epi and epi != r["epigrafe"].strip():
            r["epigrafe"] = epi
        r["correlaciones"] = correl
        r["referencias"] = parse_correl(correl)
        return r, cuerpo

    # Glosario, fracción III, numeral 40
    i = next(i for i, l in enumerate(lineas) if l.startswith("40.\tVentanilla Digital."))
    g = d["glosario"].split("\n")
    idx = [k for k, l in enumerate(g) if l.startswith("40.\tVentanilla Digital.")]
    assert len(idx) == 1, "ancla Glosario III-40"
    d.setdefault("glosario_historial", []).append({
        "numeral": "III-40", "vigente_hasta": VIG2, "fuente_anterior": ORIGINAL, "texto": g[idx[0]],
        "motivo": "Glosario, fracción III, numeral 40: " + MOT2, "resolucion": RES2})
    d.setdefault("glosario_notas_reforma", []).append("Fracción III, numeral 40 (Ventanilla Digital): " + MOT2)
    g[idx[0]] = lineas[i]
    d["glosario"] = "\n".join(g)

    # 1.4.12: reforma íntegra
    r, cuerpo = prepara("1.4.12", MOT2)
    r["texto"] = "\n".join([primera("1.4.12", cuerpo[0])] + cuerpo[1:])

    # 1.4.14: primer párrafo, fracción VIII y segundo párrafo
    r, cuerpo = prepara("1.4.14", "primer párrafo, fracción VIII y segundo párrafo: " + MOT2)
    t = r["texto"].split("\n")
    assert t[0].startswith("1.4.14. Para los efectos del artículo 162")
    t[0] = primera("1.4.14", cuerpo[0])
    assert cuerpo[1].startswith("I. a VII.")
    sustituye_linea(t, "VIII.\t", cuerpo[2], "1.4.14 fr. VIII")
    sustituye_linea(t, "\tEl expediente electrónico a que se refiere esta regla", cuerpo[3], "1.4.14 segundo párrafo")
    r["texto"] = "\n".join(t)

    # 3.1.2: se adiciona el sexto párrafo
    r, cuerpo = prepara("3.1.2", "sexto párrafo: adición de la 2a Resolución de Modificaciones a las RGCE para 2026, DOF 22-09-2026 (en vigor el 23-09-2026)")
    assert [c.strip() for c in cuerpo[:6]] == ["3.1.2.\t...".strip()] + ["..."] * 4 + [cuerpo[5].strip()] and len(cuerpo) == 6
    t = r["texto"].split("\n")
    parrafos = [l for l in t if not re.match(r"^(?:[IVX]+\.|[a-z]\))\t", l)]
    assert len(parrafos) == 5, f"3.1.2: se esperaban 5 párrafos, hay {len(parrafos)}"
    r["texto"] = r["texto"].rstrip() + "\n" + cuerpo[5]

    # 3.7.20: reforma íntegra
    r, cuerpo = prepara("3.7.20", MOT2)
    r["texto"] = "\n".join([primera("3.7.20", cuerpo[0])] + cuerpo[1:])

    # 4.5.15: segundo párrafo
    r, cuerpo = prepara("4.5.15", "segundo párrafo: " + MOT2)
    t = r["texto"].split("\n")
    assert t[1].startswith("Tratándose de la donación de mercancía"), "ancla 4.5.15 segundo párrafo"
    t[1] = cuerpo[1].strip()
    r["texto"] = "\n".join(t)

    # 4.5.33: fracción III
    r, cuerpo = prepara("4.5.33", "fracción III: " + MOT2)
    t = r["texto"].split("\n")
    sustituye_linea(t, "III.\tAviso por no arribo de mercancías", cuerpo[2], "4.5.33 fr. III")
    r["texto"] = "\n".join(t)

    # 4.6.11: primer párrafo
    r, cuerpo = prepara("4.6.11", "primer párrafo: " + MOT2)
    t = r["texto"].split("\n")
    assert t[0].startswith("4.6.11. Para los efectos de los artículos 127")
    t[0] = primera("4.6.11", cuerpo[0])
    r["texto"] = "\n".join(t)

    # 7.1.4: quinto párrafo
    r, cuerpo = prepara("7.1.4", "quinto párrafo: " + MOT2)
    t = r["texto"].split("\n")
    sustituye_linea(t, "Cuando derivado de la visita de inspección a que se refiere el párrafo anterior", cuerpo[4], "7.1.4 quinto párrafo")
    r["texto"] = "\n".join(t)

    # 7.1.5: tercer párrafo
    r, cuerpo = prepara("7.1.5", "tercer párrafo: " + MOT2)
    t = r["texto"].split("\n")
    sustituye_linea(t, "Cuando derivado de la visita de inspección resulten incumplimientos", cuerpo[2].strip(), "7.1.5 tercer párrafo")
    r["texto"] = "\n".join(t)

    # 7.2.1: tercer párrafo, fracción I y cuarto párrafo, fracción IV
    r, cuerpo = prepara("7.2.1", "tercer párrafo, fracción I y cuarto párrafo, fracción IV: " + MOT2)
    t = r["texto"].split("\n")
    sustituye_linea(t, "I.\tLas empresas que tengan observaciones respecto a los estándares mínimos de seguridad",
                    cuerpo[3], "7.2.1 tercer párrafo fr. I")
    sustituye_linea(t, "IV.\tLos contribuyentes que tengan observaciones respecto a los estándares mínimos de seguridad",
                    cuerpo[7], "7.2.1 cuarto párrafo fr. IV")
    r["texto"] = "\n".join(t)

    # Transitorio Décimo Primero (resolutivo SEGUNDO)
    ini = next(i for i, l in enumerate(lineas) if l.startswith('"Décimo'))
    fin_t = next(i for i, l in enumerate(lineas) if l.startswith("TERCERO."))
    nuevo = "\n".join(lineas[ini:fin_t]).strip().strip('"')
    reforma_transitorio(d, "Décimo\nPrimero", nuevo, VIG2, "Texto reformado por la 1a RM RGCE 2026, DOF 14-05-2026",
                        "Transitorio Décimo Primero: " + MOT2)


def entrada_id(d, id_):
    return next(x for x in d["articulos"] if x["id"] == id_)


CEDULA_RE = re.compile(r"3\. Cédula profesional con fotografía\. Quedan exceptuadas las cédulas\s+profesionales\s+electrónicas\.")
MOT_A1 = "por la Primera Modificación al Anexo 1 de las RGCE para 2026 (2a RM RGCE 2026, DOF 22-09-2026; en vigor el 23-09-2026)"
MOT_A2 = "por la Primera Modificación al Anexo 2 de las RGCE para 2026 (2a RM RGCE 2026, DOF 22-09-2026; en vigor el 23-09-2026)"
MOT_A22 = "por la Segunda Modificación al Anexo 22 de las RGCE para 2026 (2a RM RGCE 2026, DOF 22-09-2026; en vigor el 23-09-2026)"


def aplicar_rm2_anexo1(d):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_anexos import lineas_pdf, formatos_anexo1, entrada_formato

    # Contenido y apartado I, inciso a), numeral 3
    r = entrada_id(d, "RGCE-anexo-1")
    guarda_historial(r, "Apartado I, inciso a), numeral 3 derogado " + MOT_A1, VIG2, RES2)
    assert len(CEDULA_RE.findall(r["texto"])) == 1, "ancla Anexo 1, I, a), numeral 3"
    r["texto"] = CEDULA_RE.sub("3. Se deroga.", r["texto"])
    r["notas_reforma"].append(
        'Contenido, apartado II: se adiciona el renglón "E15. Información de contratos asociados a la Manifestación de Valor. '
        'AGACE/ANAM. Ventanilla Digital" y se reforman los renglones "F1. Solicitud de Expedición de Copias Certificadas de '
        'Pedimentos y sus Anexos. ANAM / DGIA. Ventanilla Digital" y "F3. Solicitud de Matriz de Seguridad para Entrega de '
        'Información de Comercio Exterior. DGMEIA. Escrito libre" ' + MOT_A1 +
        ". La tabla del Contenido en este texto conserva la versión original; ver el PDF de la modificación.")

    # formatos E15 (nuevo), F1 y F3 (reformados)
    lineas = lineas_pdf(RM2_ANEXO1)
    ini = [i for i, l in enumerate(lineas) if l.strip() == "II. Formatos de comercio exterior:"][-1]
    fin = next(i for i in range(ini, len(lineas)) if re.match(r"^\s*III\.\s*…", lineas[i]))
    nuevos = {cod: (titulo, texto) for cod, titulo, texto, _ in formatos_anexo1(lineas[ini + 1:fin], ["E15", "F1", "F3"])}
    assert set(nuevos) == {"E15", "F1", "F3"}, f"Anexo 1 mod: {sorted(nuevos)}"

    for cod in ("F1", "F3"):
        r = entrada_id(d, f"RGCE-anexo-1-{cod}")
        guarda_historial(r, f"Formato {cod} reformado " + MOT_A1, VIG2, RES2)
        r["texto"] = nuevos[cod][1]
        r.pop("nota_fuente", None)

    e15 = entrada_formato("E15", "Información de contratos asociados a la Manifestación de Valor.", nuevos["E15"][1], [])
    e15["notas_reforma"].append("Formato E15 adicionado " + MOT_A1)
    pos = next(i for i, x in enumerate(d["articulos"]) if x["id"] == "RGCE-anexo-1-F1")
    d["articulos"].insert(pos, e15)


def aplicar_rm2_anexo2(d):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_anexos import lineas_pdf, fichas_anexo2

    preambulo_mod, fichas = fichas_anexo2(lineas_pdf(RM2_ANEXO2), fin_re=re.compile(r"^Atentamente\."))
    assert len(fichas) == 37, f"Anexo 2 mod: {len(fichas)} fichas"

    r = entrada_id(d, "RGCE-anexo-2")
    guarda_historial(r, "Apartado I, inciso a), numeral 3 derogado; títulos de fichas reformadas actualizados en el Contenido " + MOT_A2, VIG2, RES2)
    assert len(CEDULA_RE.findall(r["texto"])) == 1, "ancla Anexo 2, I, a), numeral 3"
    r["texto"] = CEDULA_RE.sub("3. Se deroga.", r["texto"])

    cambios_titulo = []
    for num, titulo, texto in fichas:
        f = entrada_id(d, f"RGCE-anexo-2-{num}LA")
        guarda_historial(f, f"Ficha {num}/LA reformada " + MOT_A2, VIG2, RES2)
        if titulo != f["epigrafe"]:
            cambios_titulo.append((num, f["epigrafe"], titulo))
            # el Contenido repite el título de cada ficha
            if r["texto"].count(f["epigrafe"]) == 1:
                r["texto"] = r["texto"].replace(f["epigrafe"], titulo)
            f["epigrafe"] = titulo
        f["texto"] = texto
    return cambios_titulo


def bloque_apendice(lineas, ini, fin):
    """Quita separadores '...' / '....' y líneas vacías sobrantes al principio y al final."""
    b = [l.rstrip() for l in lineas[ini:fin]]
    while b and (not b[-1].strip() or re.fullmatch(r"\.{3,}|…", b[-1].strip())):
        b.pop()
    return b


ID_AP8_RE = re.compile(r"^([A-Z0-9]{2})\s*-")


def claves_ap8(t):
    """Posiciones de las claves del apéndice 8 (línea de clave seguida del nivel G o P)."""
    return [(i, ID_AP8_RE.match(l).group(1)) for i, l in enumerate(t[:-1])
            if ID_AP8_RE.match(l) and t[i + 1].strip() in ("G", "P")]


def aplicar_rm2_anexo22(d):
    lineas = RM2_DOC.read_text(encoding="utf-8").splitlines()
    ini = next(i for i, l in enumerate(lineas) if l.startswith("SEGUNDA MODIFICACIÓN AL ANEXO 22"))
    pos = {m: next(i for i in range(ini, len(lineas)) if lineas[i].strip() == f"Apéndice {m}") for m in (6, 8, 9, 13)}
    fin = next(i for i in range(pos[13], len(lineas)) if lineas[i].strip() == "Atentamente.")

    # Apéndices 6 y 13: se sustituyen completos
    for ap, hasta in ((6, pos[8]), (13, fin)):
        r = entrada_id(d, f"RGCE-anexo-22-ap{ap}")
        guarda_historial(r, f"Apéndice {ap} sustituido " + MOT_A22, VIG2, RES2)
        b = bloque_apendice(lineas, pos[ap], hasta)
        r["texto"] = "\n".join(b).strip()

    # Apéndice 8: AO adicionada, EX y GA reformadas
    nuevo = bloque_apendice(lineas, pos[8], pos[9])
    claves_n = claves_ap8(nuevo)
    assert [c for _, c in claves_n] == ["AO", "EX", "GA"], f"apéndice 8 mod: {claves_n}"
    bloques = {}
    for j, (i, c) in enumerate(claves_n):
        hasta = claves_n[j + 1][0] if j + 1 < len(claves_n) else len(nuevo)
        bloques[c] = bloque_apendice(nuevo, i, hasta)
    r = entrada_id(d, "RGCE-anexo-22-ap8")
    guarda_historial(r, "Clave AO adicionada y claves EX y GA reformadas " + MOT_A22, VIG2, RES2)
    t = r["texto"].split("\n")
    for c in ("EX", "GA"):
        cl = claves_ap8(t)
        k = [j for j, (_, x) in enumerate(cl) if x == c]
        assert len(k) == 1, f"apéndice 8: clave {c} x{len(k)}"
        a = cl[k[0]][0]
        b = cl[k[0] + 1][0] if k[0] + 1 < len(cl) else len(t)
        while b > a and not t[b - 1].strip():
            b -= 1
        t[a:b] = bloques[c]
    cl = claves_ap8(t)
    assert "AO" not in [x for _, x in cl], "apéndice 8: AO ya existía"
    ap_pos = next(i for i, x in cl if x == "AP")
    t[ap_pos:ap_pos] = bloques["AO"]
    r["texto"] = "\n".join(t)

    # Apéndice 9: clave C1 (SE)
    nuevo9 = bloque_apendice(lineas, pos[9], pos[13])
    c1 = nuevo9[nuevo9.index("C1") + 1]
    r = entrada_id(d, "RGCE-anexo-22-ap9")
    guarda_historial(r, "Clave C1 (Secretaría de Economía) reformada " + MOT_A22 +
                     ". Entra en vigor en términos del Transitorio Único del Acuerdo SE publicado en el DOF el 28-05-2026 "
                     "(Transitorio Segundo de la 2a RM)", VIG2, RES2)
    t = r["texto"].split("\n")
    k = [i for i in range(len(t) - 1) if t[i] == "C1" and t[i + 1].startswith("Permiso previo o permiso automático")]
    assert len(k) == 1, "ancla apéndice 9, C1"
    t[k[0] + 1] = c1
    r["texto"] = "\n".join(t)


def main():
    d = json.loads((DATA / "rgce.json").read_text(encoding="utf-8"))
    aplicadas = d.setdefault("resoluciones_aplicadas", [])

    if RM1["nombre"] not in aplicadas:
        aplicar_rm1(d)
        aplicadas.append(RM1["nombre"])
    else:
        print("La 1a RM ya estaba aplicada.")

    if RM2["nombre"] not in aplicadas:
        aplicar_rm2_reglas(d)
        aplicar_rm2_anexo1(d)
        cambios = aplicar_rm2_anexo2(d)
        aplicar_rm2_anexo22(d)
        d["ultima_reforma"] = RM2["dof"]
        aplicadas.append(RM2["nombre"])
        print("2a RM RGCE 2026 aplicada: Glosario III-40; reglas " + ", ".join(RM2["reglas_afectadas"]) +
              "; Anexo 1 (I-a-3, E15, F1, F3); Anexo 2 (I-a-3 y 37 fichas, " + str(len(cambios)) +
              " con título nuevo); Anexo 22 (ap. 6, 8, 9, 13).")
    else:
        print("La 2a RM ya estaba aplicada.")

    d["total_articulos"] = len(d["articulos"])
    (DATA / "rgce.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    # registro de resoluciones
    reg_path = DATA / "modificaciones.json"
    registro = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else []
    for rm in (RM1, RM2):
        registro = [x for x in registro if x["nombre"] != rm["nombre"]] + [rm]
    reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Registro de resoluciones:", len(registro), "entrada(s) en modificaciones.json")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
