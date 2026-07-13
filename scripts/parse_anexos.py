# -*- coding: utf-8 -*-
"""Integra los Anexos 22, 24 y 30 de las RGCE a data/rgce.json como entradas del índice.

Anexo 22: instructivo de llenado del pedimento (bloques de campos) + 22 apéndices.
Anexo 24: sistema de control de inventarios (apartados A, B y C).
Anexo 30: Sistema de Control de Cuentas de Créditos y Garantías (SCCCyG).
Correr DESPUÉS de parse_rgce.py y ANTES de aplicar_modificaciones.py.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FUENTES = BASE / "fuentes"
DATA = BASE / "data"

APENDICE_RE = re.compile(r"^Ap[ée]ndice\s+(\d+)\s*$", re.I)

APENDICE_NOMBRES = {
    "1": "Aduana-Sección", "2": "Claves de pedimento", "3": "Medios de transporte",
    "4": "Claves de países", "5": "Claves de monedas", "6": "Recintos fiscalizados",
    "7": "Unidades de medida", "8": "Identificadores", "9": "Regulaciones y restricciones no arancelarias",
    "10": "Tipos de contenedores y vehículos de autotransporte", "11": "Claves de métodos de valoración",
    "12": "Contribuciones, cuotas compensatorias, gravámenes y derechos",
    "13": "Formas de pago", "14": "Términos de facturación", "15": "Destinos de mercancía",
    "16": "Regímenes", "17": "Código de barras, pedimentos, partes II y copia simple, consolidados",
    "18": "Tipos de tasas", "19": "Clasificación de las sustancias peligrosas", "20": "Pago electrónico",
    "21": "Administradores y operadores de recintos fiscalizados estratégicos",
    "22": "Características tecnológicas de dispositivos con tecnología de radiofrecuencia",
}


def entrada(id_, numero, epigrafe, texto, cap_nombre, formato="pre"):
    return {
        "id": id_, "numero": numero, "epigrafe": epigrafe,
        "titulo": None, "titulo_nombre": None,
        "capitulo": "ANEXOS", "capitulo_nombre": cap_nombre,
        "seccion": None, "seccion_nombre": None,
        "notas_reforma": [], "historial": [], "referencias": [],
        "correlaciones": "", "formato": formato, "texto": texto,
    }


def main():
    lines = (FUENTES / "rgce2026_anexos21a30_dof.txt").read_text(encoding="cp1252").splitlines()
    idx22 = next(i for i, l in enumerate(lines) if l.strip().startswith("ANEXO 22 DE LAS"))
    idx23 = next(i for i, l in enumerate(lines) if l.strip().startswith("ANEXO 23 DE LAS"))
    idx24 = next(i for i, l in enumerate(lines) if l.strip().startswith("ANEXO 24 DE LAS"))
    idx25 = next(i for i, l in enumerate(lines) if l.strip().startswith("ANEXO 25 DE LAS"))
    idx30 = next(i for i, l in enumerate(lines) if l.strip().startswith("ANEXO 30 DE LAS"))
    a22 = [l.rstrip() for l in lines[idx22:idx23]]
    a24 = [l.rstrip() for l in lines[idx24:idx25]]
    a30 = [l.rstrip() for l in lines[idx30:]]
    # recorta el cierre del DOF ("Atentamente." y pies de página)
    fin30 = next((i for i, l in enumerate(a30) if l.strip().startswith("Atentamente")), len(a30))
    a30 = a30[:fin30]

    # --- Anexo 22: separar instructivo y apéndices
    cortes = [(i, APENDICE_RE.match(l.strip()).group(1)) for i, l in enumerate(a22) if APENDICE_RE.match(l.strip())]
    # el instructivo va del inicio al primer 'Apéndice 1'
    fin_instr = cortes[0][0]
    instructivo = "\n".join(l for l in a22[:fin_instr]).strip()

    entradas = [entrada(
        "RGCE-anexo-22", "Anexo 22", "Instructivo para el llenado del pedimento — Campos",
        instructivo, "Anexo 22 — Instructivo del pedimento")]

    # agrupar cortes por apéndice (el título puede aparecer duplicado)
    vistos = {}
    for pos, num in cortes:
        vistos.setdefault(num, pos)  # primera aparición
    ordenados = sorted(vistos.items(), key=lambda x: x[1])
    for j, (num, pos) in enumerate(ordenados):
        fin = ordenados[j + 1][1] if j + 1 < len(ordenados) else len(a22)
        texto = "\n".join(a22[pos:fin]).strip()
        nombre = APENDICE_NOMBRES.get(num, "")
        entradas.append(entrada(
            f"RGCE-anexo-22-ap{num}", f"Anexo 22 · Apéndice {num}", nombre,
            texto, "Anexo 22 — Apéndices"))

    # --- Anexo 24 completo
    entradas.append(entrada(
        "RGCE-anexo-24", "Anexo 24",
        "Información mínima del sistema automatizado de control de inventarios (IMMEX)",
        "\n".join(a24).strip(), "Anexo 24 — Control de inventarios"))

    # --- Anexo 30 completo
    entradas.append(entrada(
        "RGCE-anexo-30", "Anexo 30",
        "Sistema de Control de Cuentas de Créditos y Garantías (SCCCyG)",
        "\n".join(a30).strip(), "Anexo 30 — SCCCyG"))

    d = json.loads((DATA / "rgce.json").read_text(encoding="utf-8"))
    d["articulos"] = [a for a in d["articulos"] if not a["id"].startswith("RGCE-anexo-")]
    d["articulos"].extend(entradas)
    d["total_articulos"] = len(d["articulos"])
    d["anexos_fuente"] = "DOF 15-01-2026 (Anexos 21 a 30 de las RGCE para 2026)"
    (DATA / "rgce.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Anexo 22: instructivo ({len(instructivo)//1024} KB) + {len(ordenados)} apéndices | "
          f"Anexo 24: {len(a24)} líneas | Anexo 30: {len(a30)} líneas | total entradas RGCE: {len(d['articulos'])}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
