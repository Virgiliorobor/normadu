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


def regla(d, num):
    return next(r for r in d["articulos"] if r["numero"] == num)


def guarda_historial(r, motivo):
    r["historial"].append({
        "vigente_hasta": "14-05-2026",
        "fuente_anterior": "RGCE 2026 original, DOF 27-12-2025",
        "texto": r["texto"],
        "correlaciones": r.get("correlaciones", ""),
        "motivo": motivo,
    })
    if NOTA not in r["notas_reforma"]:
        r["notas_reforma"].append(motivo)


def parse_correl(texto):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from parse_rgce import parse_correlaciones
    return parse_correlaciones(texto)


def main():
    d = json.loads((DATA / "rgce.json").read_text(encoding="utf-8"))

    if d.get("ultima_reforma") == RM1["dof"]:
        print("La 1a RM ya estaba aplicada; nada que hacer.")
        return

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
    m = re.search(r"Décimo\nPrimero\.\t.*?(?=\nDécimo\nSegundo\.)", d["transitorios"], re.S)
    assert m, "ancla Transitorio Décimo Primero no encontrada"
    d["transitorios"] = d["transitorios"][:m.start()] + NUEVO_TRANS_11 + d["transitorios"][m.end():]

    d["ultima_reforma"] = RM1["dof"]

    (DATA / "rgce.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    # registro de resoluciones
    reg_path = DATA / "modificaciones.json"
    registro = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else []
    if not any(x["nombre"] == RM1["nombre"] for x in registro):
        registro.append(RM1)
    reg_path.write_text(json.dumps(registro, ensure_ascii=False, indent=1), encoding="utf-8")

    print("1a RM RGCE 2026 aplicada: reglas 1.4.14, 1.5.1, 4.8.2, 4.8.4 y Transitorio Décimo Primero.")
    print("Registro de resoluciones:", len(registro), "entrada(s) en modificaciones.json")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
