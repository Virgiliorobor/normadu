# -*- coding: utf-8 -*-
"""Integra los Anexos 1, 2, 22, 24 y 30 de las RGCE a data/rgce.json como entradas del índice.

Anexo 1: formatos y modelos (contenido + identificaciones, y una entrada por formato A1…M1.11).
Anexo 2: fichas de trámite (contenido + identificaciones, y una entrada por ficha 1/LA…150/LA).
Anexo 22: instructivo de llenado del pedimento (bloques de campos) + 22 apéndices.
Anexo 24: sistema de control de inventarios (apartados A, B y C).
Anexo 30: Sistema de Control de Cuentas de Créditos y Garantías (SCCCyG).
Correr DESPUÉS de parse_rgce.py y ANTES de aplicar_modificaciones.py.

Los Anexos 1 y 2 vienen del PDF del minisitio SAT (misma publicación del DOF; el .doc
del DOF del Anexo 1 solo contiene imágenes de página). Texto extraído con pdftotext:
Anexo 1 en modo -layout (formatos), Anexo 2 en modo normal.
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


# --- utilidades para texto extraído de PDF del DOF (pdftotext)

DIAS = r"(?:Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)"
ENCABEZADO_RE = re.compile(
    rf"^(?:\d+\s+)?(?:(?:DIARIO OFICIAL|{DIAS}\s+\d+\s+de\s+\w+\s+de\s+\d{{4}})\s*)+(?:\d+)?$")
ENCABEZADO_EN_LINEA_RE = re.compile(rf"(?:^|\s{{2,}})(?:DIARIO OFICIAL|{DIAS}\s+\d+\s+de\s+\w+\s+de\s+\d{{4}})(?=\s{{2,}}|$)")


def lineas_pdf(path):
    """Lee un .txt de pdftotext y quita saltos de página y encabezados del DOF."""
    out = []
    for l in path.read_text(encoding="utf-8").replace("\f", "\n").splitlines():
        l = l.rstrip()
        if ENCABEZADO_RE.match(l.strip()):
            continue
        # en páginas apaisadas (modo -layout) el encabezado queda en la misma línea que el texto
        l = ENCABEZADO_EN_LINEA_RE.sub("", l).rstrip()
        out.append(l)
    return out


def compacta(lineas):
    """Une las líneas en texto, sin líneas vacías repetidas ni separadores '…' al final."""
    texto = re.sub(r"\n{3,}", "\n\n", "\n".join(lineas)).strip()
    return re.sub(r"(\n\s*…\s*)+$", "", texto).strip()


# --- Anexo 2: fichas de trámite

FICHA_RE = re.compile(r"^(\d{1,3})/LA\s+(\S.*)$")


def fichas_anexo2(lineas, fin_re=None):
    """Divide el texto del Anexo 2 en fichas. Devuelve (preambulo, [(num, titulo, texto)]).

    Una ficha empieza en una línea '<n>/LA <título>' con n creciente (así se descartan las
    menciones del contenido y las citas dentro de otras fichas). El título puede seguir en
    las líneas siguientes hasta la primera línea vacía."""
    def abre_ficha(i):
        # toda ficha abre con el recuadro "Trámite / Servicio"
        siguientes = [x.strip() for x in lineas[i + 1:i + 12] if x.strip()][:6]
        return any(x.startswith("Trámite") for x in siguientes)

    inicios, ultimo = [], 0
    for i, l in enumerate(lineas):
        m = FICHA_RE.match(l.strip())
        if m and int(m.group(1)) > ultimo and abre_ficha(i):
            inicios.append((i, m.group(1)))
            ultimo = int(m.group(1))
    fin = len(lineas)
    if fin_re is not None:
        fin = next((i for i, l in enumerate(lineas) if i > (inicios[-1][0] if inicios else 0) and fin_re.match(l.strip())), fin)
    fichas = []
    for j, (pos, num) in enumerate(inicios):
        hasta = inicios[j + 1][0] if j + 1 < len(inicios) else fin
        bloque = lineas[pos:hasta]
        titulo = []
        for l in bloque:
            if not l.strip():
                break
            titulo.append(l.strip())
        titulo = re.sub(r"\s+", " ", " ".join(titulo))
        titulo = re.sub(rf"^{num}/LA\s+", "", titulo)
        fichas.append((num, titulo, compacta(bloque)))
    preambulo = compacta(lineas[:inicios[0][0]]) if inicios else compacta(lineas)
    return preambulo, fichas


def entrada_ficha(num, titulo, texto):
    return entrada(f"RGCE-anexo-2-{num}LA", f"Anexo 2 · {num}/LA", titulo, texto,
                   "Anexo 2 — Fichas de trámite")


def anexo2():
    lineas = lineas_pdf(FUENTES / "rgce2026_anexo2_dof_20260112.txt")
    preambulo, fichas = fichas_anexo2(lineas, fin_re=re.compile(r"^Atentamente\."))
    assert len(fichas) == 150 and fichas[-1][0] == "150", f"Anexo 2: {len(fichas)} fichas"
    entradas = [entrada("RGCE-anexo-2", "Anexo 2",
                        "Trámites de comercio exterior — Contenido, identificaciones oficiales y comprobantes de domicilio",
                        preambulo, "Anexo 2 — Fichas de trámite")]
    entradas += [entrada_ficha(n, t, x) for n, t, x in fichas]
    return entradas


# --- Anexo 1: formatos y modelos

CODIGOS_ANEXO1 = ([f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 19)] +
                  [f"C{i}" for i in range(1, 4)] + [f"D{i}" for i in range(1, 10)] +
                  [f"E{i}" for i in range(1, 15)] + [f"F{i}" for i in range(1, 4)] +
                  [f"M1.{i}" for i in range(1, 12)])
FORMATO_RE = re.compile(r"^\s*([A-F]\d{1,2}|M1\.\d{1,2})(?:\.(?:\s|$)|\s*$)")

# Nombres tomados del Contenido del Anexo 1 (DOF 08-01-2026); el cuerpo del PDF no siempre
# repite el nombre junto al rótulo.
NOMBRES_ANEXO1 = {
    "A1": "Autorización de importación temporal.",
    "A2": "Autorización de importación temporal de embarcaciones/ Authorization for temporal importation of boats.",
    "A3": "Autorización de importación temporal de mercancías, destinadas al mantenimiento y reparación de las mercancías importadas temporalmente.",
    "A4": "Autorización para importar mercancía por única vez, sin haber concluido el trámite de inscripción o estando suspendidos en el Padrón de Importadores, (Regla 1.3.5.).",
    "A5": "Autorización a personas físicas para importar mercancía por única vez, sin estar inscritas en el Padrón de Importadores, (Regla 1.3.6.).",
    "A6": "Autorización de inscripción para el Padrón de Exportadores Sectorial (Regla 1.3.7.).",
    "A7": "Autorización para la importación de vehículos especialmente construidos o transformados, equipados con dispositivos o aparatos diversos para cumplir con contrato derivado de licitación pública, (Regla 4.2.9.).",
    "A8": "Autorización de rectificación de pedimentos.",
    "A9": "Autorización para importar mercancías con fines de seguridad nacional.",
    "A10": "Importación temporal de las mercancías destinadas a la CMF 2026 y sus eventos relacionados.",
    "B1": "Aviso de compensación de contribuciones y aprovechamientos al comercio exterior.",
    "B2": "Aviso de exportación temporal.",
    "B3": "Aviso de importación o exportación temporal y retorno de envases.",
    "B4": "Aviso de introducción de mercancía donada a la franja fronteriza del país (Regla 3.3.6., fracción II).",
    "B5": "Aviso para prorrogar el plazo otorgado por la SE para cambiar al régimen de importación definitiva o retornar al extranjero mercancías importadas temporalmente (4.3.8.).",
    "B6": "Aviso para el traslado de autopartes ubicadas en la franja o región fronteriza a la industria terminal automotriz o manufacturera de vehículos de autotransporte en el resto del territorio nacional.",
    "B7": "Aviso de opción para la determinación del valor provisional (seguro global de transporte).",
    "B8": "Aviso de registro de aparatos electrónicos e instrumentos de trabajo.",
    "B9": "Aviso de transferencia de mercancías sujetas al régimen de depósito fiscal de Duty Free.",
    "B10": "Aviso de traslado de mercancías de empresas con Programa IMMEX, RFE u Operador Económico Autorizado.",
    "B11": "Aviso de traslado de mercancías de empresas con Programa IMMEX en la modalidad de Operador Económico Autorizado rubro controladora de empresas.",
    "B12": "Aviso electrónico de importación y de exportación.",
    "B13": "Aviso de Capacidad Volumétrica de Almacenaje (Regla 2.3.8.).",
    "B14": "Encargo conferido al agente aduanal para realizar operaciones de comercio exterior o la revocación del mismo.",
    "B15": "Encargo conferido a la agencia aduanal para realizar operaciones de comercio exterior o la revocación del mismo.",
    "B16": "Aviso electrónico de rechazo (Regla 1.8.2.).",
    "B17": "Aviso de retorno seguro de vehículos extranjeros.",
    "B18": "Aviso de exportación temporal de artesanías.",
    "C1": "Constancia de importación temporal, retorno o transferencia de contenedores.",
    "C2": "Constancia de origen de productos agropecuarios.",
    "C3": "Constancia de transferencia de mercancías.",
    "D1": "Formulario Postal.",
    "D2": "Declaración de aduana para pasajeros procedentes del extranjero (Español e Inglés).",
    "D3": "Declaración de dinero salida de pasajeros (Español e Inglés).",
    "D4": "Declaración de Internación o Extracción de cantidades en efectivo y/o documentos por cobrar (Español e Inglés).",
    "D5": "Declaración para Movimiento en Cuenta Aduanera de Bienes, Importados Para Retornar en su Mismo Estado conforme al Art. 86 de la L.A.",
    "D6": "Documento de origen de productos minerales extraídos, industrializados o manufacturados.",
    "D7": "Pago de contribuciones al comercio exterior (Español, Inglés y Francés).",
    "D8": "Pedimento de importación temporal de remolques, semirremolques y portacontenedores.",
    "D9": "Formulario múltiple de pago para comercio exterior.",
    "E1": "Engomado oficial para el control de tránsito interno por vía aérea.",
    "E2": "Manifestación de Valor.",
    "E3": "Perfil de la empresa.",
    "E4": "Perfil del Agente Aduanal.",
    "E5": "Perfil del Auto transportista Terrestre.",
    "E6": "Perfil de Mensajería y Paquetería.",
    "E7": "Perfil del Recinto Fiscalizado.",
    "E8": "Perfil del Recinto Fiscalizado Estratégico.",
    "E9": "Perfil del Transportista Ferroviario.",
    "E10": "Perfil de Parques Industriales.",
    "E11": "Perfil del Almacén General de Depósito.",
    "E12": "Manifestación de voluntad para asumir la responsabilidad solidaria en términos de la regla 7.3.3., fracción XIII.",
    "E13": "Solicitud de emisión de resolución anticipada.",
    "E14": "Formato para presentar el Dictamen de compensación o disminución de gastos contra el aprovechamiento a cargo.",
    "F1": "Solicitud de Expedición de Copias Certificadas de Pedimentos y sus Anexos.",
    "F2": "Solicitud de usuario y contraseña para ingresar al Sistema de Operación Integral Aduanera (SOIA).",
    "F3": "Solicitud de Matriz de Seguridad para Entrega de Información de Comercio Exterior.",
    "M1.1": "Pedimento.",
    "M1.2": "Pedimento de importación. Parte II. Embarque parcial de mercancías.",
    "M1.3": "Pedimento de exportación. Parte II. Embarque parcial de mercancías.",
    "M1.4": "Pedimento de tránsito para el transbordo.",
    "M1.5": "Forma Simplificada del Pedimento.",
    "M1.6": "Formato de Aviso consolidado.",
    "M1.7": "Documento de operación para despacho aduanero (DODA).",
    "M1.8": "Carta de cupo electrónica.",
    "M1.9": "Carta de cupo para exposiciones internacionales.",
    "M1.10": "Reporte de exportaciones de operaciones de submanufactura o submaquila.",
    "M1.11": "Relación de documentos.",
}


def formatos_anexo1(lineas, codigos):
    """Divide el cuerpo del Anexo 1 en formatos. Un formato empieza en una línea '<código>.'
    cuyo código va después del último encontrado en `codigos`. Devuelve
    [(codigo, titulo, texto, codigos_sin_rotulo)]: los códigos sin rótulo propio en el
    texto fuente quedan dentro del formato anterior y se informan."""
    orden = {c: k for k, c in enumerate(codigos)}
    inicios, ultimo = [], -1
    for i, l in enumerate(lineas):
        m = FORMATO_RE.match(l)
        if m and m.group(1) in orden and orden[m.group(1)] > ultimo:
            inicios.append((i, m.group(1)))
            ultimo = orden[m.group(1)]
    out = []
    for j, (pos, cod) in enumerate(inicios):
        hasta = inicios[j + 1][0] if j + 1 < len(inicios) else len(lineas)
        sig = orden[inicios[j + 1][1]] if j + 1 < len(inicios) else len(codigos)
        faltan = codigos[orden[cod] + 1:sig]
        out.append((cod, NOMBRES_ANEXO1.get(cod, ""), compacta(lineas[pos:hasta]), faltan))
    return out


def entrada_formato(cod, titulo, texto, faltan):
    e = entrada(f"RGCE-anexo-1-{cod}", f"Anexo 1 · {cod}", titulo, texto,
                "Anexo 1 — Formatos y modelos")
    notas = []
    if len(texto) < 20:
        notas.append("Formato publicado como imagen en el DOF: sin texto extraíble. Consultar "
                     "fuentes/rgce2026_anexo1_dof_20260108.pdf.")
    if faltan:
        notas.append("El texto fuente no rotula por separado " + ", ".join(faltan) +
                     "; su contenido, si lo tiene en texto, queda dentro de esta entrada. Consultar el PDF.")
    if notas:
        e["nota_fuente"] = " ".join(notas)
    return e


def anexo1():
    lineas = lineas_pdf(FUENTES / "rgce2026_anexo1_dof_20260108_layout.txt")
    # el cuerpo empieza en la segunda aparición de "II. Formatos de comercio exterior:"
    apariciones = [i for i, l in enumerate(lineas) if l.strip().startswith("II. Formatos de comercio exterior:")]
    inicio_cuerpo = apariciones[1]
    fin = next(i for i in range(len(lineas) - 1, 0, -1) if lineas[i].strip() == "Atentamente.")
    formatos = formatos_anexo1(lineas[inicio_cuerpo + 1:fin], CODIGOS_ANEXO1)
    assert formatos[0][0] == "A1" and formatos[-1][0] == "M1.11", "Anexo 1: rótulos A1/M1.11 no encontrados"
    entradas = [entrada("RGCE-anexo-1", "Anexo 1",
                        "Formatos y modelos de comercio exterior — Contenido, identificaciones oficiales y comprobantes de domicilio",
                        compacta(lineas[:inicio_cuerpo + 1]), "Anexo 1 — Formatos y modelos")]
    entradas += [entrada_formato(*f) for f in formatos]
    return entradas


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

    a1 = anexo1()
    a2 = anexo2()
    entradas = a1 + a2 + [entrada(
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
    d["anexos_fuente"] = ("Anexo 1: DOF 08-01-2026; Anexo 2: DOF 12-01-2026 (PDF del minisitio SAT); "
                          "Anexos 22, 24 y 30: DOF 15-01-2026 (Anexos 21 a 30 de las RGCE para 2026)")
    (DATA / "rgce.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")

    con_nota = [e["numero"].split("· ")[-1] for e in a1 if e.get("nota_fuente")]
    print(f"Anexo 1: {len(a1) - 1} formatos (con nota de fuente: {', '.join(con_nota) or 'ninguno'}) | "
          f"Anexo 2: {len(a2) - 1} fichas")
    print(f"Anexo 22: instructivo ({len(instructivo)//1024} KB) + {len(ordenados)} apéndices | "
          f"Anexo 24: {len(a24)} líneas | Anexo 30: {len(a30)} líneas | total entradas RGCE: {len(d['articulos'])}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
