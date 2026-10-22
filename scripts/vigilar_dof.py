# -*- coding: utf-8 -*-
"""Vigilancia de publicaciones: revisa el DOF (API pública de SIDOF) día por día desde la
última reforma de cada ordenamiento de data/index.json, más las versiones anticipadas del
minisitio del SAT y la fecha de última reforma de LeyesBiblio, y escribe un reporte corto
de lo que cambió y lo que falta aplicar.

Uso:
    python scripts/vigilar_dof.py                 # desde la última reforma de cada ordenamiento
    python scripts/vigilar_dof.py --desde 01-09-2026 --hasta 22-10-2026

Salida: vigilancia/reporte_AAAAMMDD.md (y copia en vigilancia/ultimo_reporte.md).
Código de salida 0 = nada pendiente; 2 = hay publicaciones por revisar.

Las notas ya revisadas se marcan en vigilancia/atendidas.json ({codNota: "aplicada" | "no aplica"
| "registrada" | ...}, con una nota libre); esas ya no aparecen como pendientes.
Las respuestas del DOF de días con más de 7 días de antigüedad se guardan en .cache/sidof/.
No requiere servicios de pago ni llaves: solo urllib de la biblioteca estándar.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SALIDA = BASE / "vigilancia"
CACHE = BASE / ".cache" / "sidof"

SIDOF_DIA = "https://sidof.segob.gob.mx/dof/sidof/notas/{}"
SIDOF_FICHA = "https://sidof.segob.gob.mx/notas/{}"
DOF_NOTA = "https://www.dof.gob.mx/nota_detalle.php?codigo={}&fecha={}"
DOF_PAGINA = "https://dof.gob.mx/nota_detalle.php?codigo={}&fecha={}"  # sin www: el certificado de www no coincide
SAT_2026 = "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/normatividad_rmf_rgce{}.html"
LEYESBIBLIO_PDF = {"LA": "https://www.diputados.gob.mx/LeyesBiblio/pdf/LAdua.pdf",
                   "RLA": "https://www.diputados.gob.mx/LeyesBiblio/regley/Reg_LAdua.pdf"}
UA = {"User-Agent": "normadu-vigilancia/1.0 (consulta de publicaciones oficiales)"}

# Patrones sobre el título normalizado (sin acentos, minúsculas). Un título puede caer en varios.
VIGILA = {
    "LA": [r"(?<!reglamento de la )\bley aduanera\b"],
    "RLA": [r"reglamento de la ley aduanera"],
    "RGCE": [r"reglas generales de comercio exterior"],
    "RCSE": [r"reglas y criterios de caracter general en materia de comercio exterior"],
    "IMMEX": [r"\bimmex\b", r"industria manufacturera, maquiladora y de servicios de exportacion"],
}
# Relacionado, fuera del corpus: se lista aparte para que el owner decida.
RELACIONADO = [r"comercio exterior", r"aduan", r"arancel", r"impuestos generales de importacion",
               r"cuota compensatoria", r"\bcupo", r"prosec", r"tratado", r"t-mec", r"origen",
               r"padron de importadores", r"recinto fiscalizado", r"programa de promocion sectorial"]
# Publicaciones periódicas que mencionan un ordenamiento pero no lo reforman.
EXCLUYE = [r"^aviso por el que se dan a conocer los nombres de los titulares"]
DEPENDENCIAS = ("HACIENDA", "ECONOMIA", "TRIBUTARIA")  # notas sin título de estas dependencias
DIAS_SIN_TITULO = 14  # las notas sin título solo se listan si son de los últimos N días


def norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def get(url, timeout=40, intentos=3):
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            if i == intentos - 1:
                raise
            time.sleep(2 * (i + 1))


def notas_del_dia(d):
    """Todas las notas (matutina, vespertina, extraordinaria) de una fecha del DOF."""
    clave = d.strftime("%d-%m-%Y")
    f = CACHE / f"{clave}.json"
    if f.exists():
        datos = json.loads(f.read_text(encoding="utf-8"))
    else:
        datos = json.loads(get(SIDOF_DIA.format(clave)))
        if (date.today() - d).days > 7:
            CACHE.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        time.sleep(0.3)
    notas = []
    for edicion in ("NotasMatutinas", "NotasVespertinas", "NotasExtraordinarias"):
        for n in datos.get(edicion) or []:
            n["_edicion"] = edicion.replace("Notas", "")
            notas.append(n)
    return notas


def titulo_dof(cod, fecha_nota):
    """Título de una nota leído de la página de dof.gob.mx (SIDOF no lo trae para algunas notas)."""
    try:
        h = get(DOF_PAGINA.format(cod, fecha_nota.replace("-", "/"))).decode("utf-8", "replace")
    except Exception:
        return ""
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    if "únicamente puede ser visualizado a través de la edición" in t:
        return "(solo PDF de la edición; sin título en SIDOF ni en dof.gob.mx)"
    m = re.search(r"DOF:\s*\d\d/\d\d/\d{4}\s+(.{5,400}?)(?:\s+\.\w+\s*\{|Al margen)", t, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def fecha(s):
    return datetime.strptime(s, "%d-%m-%Y").date()


def revisar_dof(desde_por_ord, hasta, atendidas):
    desde = min(desde_por_ord.values())
    hallazgos, relacionadas, sin_titulo, fallidos = [], [], [], []
    d = desde
    while d <= hasta:
        try:
            notas = notas_del_dia(d)
        except Exception as e:
            fallidos.append(f"{d:%d-%m-%Y}: {e}")
            d += timedelta(days=1)
            continue
        for n in notas:
            titulo = n.get("titulo") or ""
            org = n.get("codOrgaDos") or ""
            if not titulo and any(x in org for x in DEPENDENCIAS) and (hasta - d).days < DIAS_SIN_TITULO:
                titulo = titulo_dof(n["codNota"], n["fecha"])
            t = norm(titulo)
            item = {
                "codNota": n["codNota"], "fecha": n["fecha"], "edicion": n["_edicion"],
                "dependencia": org, "titulo": titulo.strip(),
                "url": DOF_NOTA.format(n["codNota"], n["fecha"].replace("-", "/")),
                "doc": n.get("existeDoc") == "S",
                "atendida": atendidas.get(str(n["codNota"])),
            }
            ords = [o for o, pats in VIGILA.items()
                    if any(re.search(p, t) for p in pats) and d > desde_por_ord.get(o, desde)]
            if any(re.search(p, t) for p in EXCLUYE):
                continue
            if ords:
                item["ordenamientos"] = ords
                hallazgos.append(item)
            elif not n.get("titulo") and any(x in org for x in DEPENDENCIAS):
                sin_titulo.append(item)
            elif any(x in org for x in DEPENDENCIAS) and any(re.search(p, t) for p in RELACIONADO):
                relacionadas.append(item)
        d += timedelta(days=1)
    return hallazgos, relacionadas, sin_titulo, fallidos


def revisar_sat(anio, conocidos):
    """Documentos de RGCE en el minisitio del SAT que no estaban en la corrida anterior."""
    html = get(SAT_2026.format(anio)).decode("utf-8", "replace")
    docs = sorted(set(re.findall(r'href="(documentos%s/rgce/[^"]+)"' % anio, html)))
    nuevos = [x for x in docs if x not in conocidos]
    return docs, nuevos


def revisar_leyesbiblio():
    """'Última reforma publicada DOF dd-mm-aaaa' de la portada del PDF de LeyesBiblio (LA y RLA).
    El índice HTML de LeyesBiblio no sirve: su segunda fecha puede ser la de cantidades actualizadas."""
    out = {}
    CACHE.mkdir(parents=True, exist_ok=True)
    for ord_, url in LEYESBIBLIO_PDF.items():
        pdf = CACHE.parent / f"leyesbiblio_{ord_}.pdf"
        try:
            pdf.write_bytes(get(url, timeout=120))
            txt = subprocess.run(["pdftotext", "-l", "1", "-enc", "UTF-8", str(pdf), "-"],
                                 capture_output=True, check=True).stdout.decode("utf-8", "replace")
        except Exception as e:
            out[ord_] = f"error: {e}"
            continue
        m = re.search(r"[ÚU]ltima reforma publicada DOF\s+(\d{2}-\d{2}-\d{4})", txt, re.I)
        out[ord_] = m.group(1) if m else "sin fecha legible"
    return out


def solo_en_linea(raiz):
    """Archivos del corpus que OneDrive dejó 'solo en línea' (atributos RECALL_ON_DATA_ACCESS u OFFLINE).
    No se abren: solo se lee el atributo, así que no se descargan."""
    if not hasattr(os.stat_result, "st_file_attributes"):
        return []
    fuera = {"opiniones", "intake", "worktrees", ".cache"}
    out = []
    for dirpath, dirnames, files in os.walk(raiz):
        dirnames[:] = [x for x in dirnames if x not in fuera]
        for f in files:
            p = Path(dirpath) / f
            try:
                if os.stat(p, follow_symlinks=False).st_file_attributes & 0x401000:
                    out.append(str(p.relative_to(raiz)))
            except OSError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="DD-MM-AAAA; por omisión, la última reforma de cada ordenamiento")
    ap.add_argument("--hasta", default=date.today().strftime("%d-%m-%Y"))
    ap.add_argument("--sin-sat", action="store_true")
    ap.add_argument("--sin-leyesbiblio", action="store_true")
    a = ap.parse_args()

    SALIDA.mkdir(exist_ok=True)
    index = json.loads((DATA / "index.json").read_text(encoding="utf-8"))
    ultima = {o["id"]: fecha(o["ultima_reforma"]) for o in index["ordenamientos"]}
    desde_por_ord = {k: fecha(a.desde) for k in ultima} if a.desde else ultima
    hasta = fecha(a.hasta)
    f_at = SALIDA / "atendidas.json"
    atendidas = json.loads(f_at.read_text(encoding="utf-8")) if f_at.exists() else {}
    f_estado = SALIDA / "estado.json"
    estado = json.loads(f_estado.read_text(encoding="utf-8")) if f_estado.exists() else {}

    hallazgos, relacionadas, sin_titulo, fallidos = revisar_dof(desde_por_ord, hasta, atendidas)
    pendientes = [h for h in hallazgos if not h["atendida"]]

    sat_docs, sat_nuevos, sat_error = [], [], None
    if not a.sin_sat:
        try:
            sat_docs, sat_nuevos = revisar_sat(hasta.year, set(estado.get("sat_docs", [])))
        except Exception as e:
            sat_error = str(e)
    lb = {} if a.sin_leyesbiblio else revisar_leyesbiblio()

    L = [f"# Vigilancia normadu — {date.today():%d-%m-%Y}", "",
         f"DOF revisado (SIDOF) hasta el {hasta:%d-%m-%Y}, desde la última reforma de cada ordenamiento:",
         ""]
    L += [f"- {k}: desde {v:%d-%m-%Y}" for k, v in desde_por_ord.items()]
    L += ["", f"## Pendientes de aplicar o descartar ({len(pendientes)})", ""]
    L += [f"- **{', '.join(h['ordenamientos'])}** · DOF {h['fecha']} ({h['edicion']}) · {h['dependencia']}\n"
          f"  {h['titulo']}\n  {h['url']}" for h in pendientes] or ["Ninguna."]
    hechas = [h for h in hallazgos if h["atendida"]]
    if hechas:
        L += ["", "## Ya atendidas", ""]
        L += [f"- {', '.join(h['ordenamientos'])} · DOF {h['fecha']} · {h['atendida']} · {h['titulo'][:140]}"
              for h in hechas]
    L += ["", "## SAT, minisitio RGCE (versiones anticipadas y compilados)", ""]
    if sat_error:
        L.append(f"Error al consultar: {sat_error}")
    elif a.sin_sat:
        L.append("No consultado.")
    elif not estado.get("sat_docs"):
        L.append(f"Primera corrida: {len(sat_docs)} documentos registrados como línea base.")
    else:
        L += [f"- NUEVO: https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/{x}" for x in sat_nuevos] \
            or ["Sin documentos nuevos desde la corrida anterior."]
    L += ["", "Una versión anticipada no se aplica a `data\\` hasta que se publique en el DOF (regla 1.1.2)."]
    if lb:
        L += ["", "## LeyesBiblio (Cámara de Diputados), última reforma mostrada", ""]
        for k, v in lb.items():
            marca = "" if v == f"{ultima[k]:%d-%m-%Y}" else "  ← distinta del corpus, revisar"
            L.append(f"- {k}: {v} (corpus: {ultima[k]:%d-%m-%Y}){marca}")
    # relacionadas: solo lo publicado después de la corrida anterior (o los últimos 30 días en la primera)
    previo = fecha(estado["dof_hasta"]) if estado.get("dof_hasta") else hasta - timedelta(days=30)
    if previo >= hasta:
        previo = hasta - timedelta(days=7)
    nuevas = [h for h in relacionadas if fecha(h["fecha"]) > previo]
    if nuevas:
        L += ["", f"## Relacionadas, fuera del corpus, publicadas después del {previo:%d-%m-%Y} ({len(nuevas)})", ""]
        L += [f"- DOF {h['fecha']} · {h['dependencia']} · {h['titulo'][:180]}\n  {h['url']}" for h in nuevas]
    recientes = [h for h in sin_titulo if (hasta - fecha(h["fecha"])).days < DIAS_SIN_TITULO]
    if sin_titulo:
        L += ["", f"## Notas sin título en SIDOF de SHCP/SE/SAT: {len(sin_titulo)} en el periodo; "
                  f"{len(recientes)} de los últimos {DIAS_SIN_TITULO} días (título leído de dof.gob.mx)", ""]
        L += [f"- DOF {h['fecha']} · {h['dependencia']} · {(h['titulo'] or 'sin título legible')[:160]}\n"
              f"  {SIDOF_FICHA.format(h['codNota'])}" for h in recientes]
    if fallidos:
        L += ["", "## Días que no se pudieron consultar (volver a correr)", ""] + [f"- {x}" for x in fallidos]
    nube = solo_en_linea(BASE)
    L += ["", f"## Archivos solo en línea (OneDrive): {len(nube)}", ""]
    if nube:
        L += [f"- {x}" for x in nube[:20]] + ([f"- … y {len(nube) - 20} más"] if len(nube) > 20 else [])
        L.append("Para dejarlos en el disco: Explorador > clic derecho en la carpeta > «Mantener siempre en este dispositivo».")
    L += ["", "Copia de trabajo: el sustento legal es la publicación del DOF."]

    texto = "\n".join(L) + "\n"
    (SALIDA / f"reporte_{date.today():%Y%m%d}.md").write_text(texto, encoding="utf-8")
    (SALIDA / "ultimo_reporte.md").write_text(texto, encoding="utf-8")
    if sat_docs:
        estado["sat_docs"] = sat_docs
    estado["ultima_corrida"] = date.today().isoformat()
    estado["dof_hasta"] = f"{hasta:%d-%m-%Y}"
    f_estado.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(texto)
    return 2 if (pendientes or sat_nuevos or fallidos) else 0


if __name__ == "__main__":
    sys.exit(main())
