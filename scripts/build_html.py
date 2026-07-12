# -*- coding: utf-8 -*-
"""Genera normativa.html (visor autocontenido) a partir de data/*.json."""
import json
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
SALIDA = BASE / "normativa.html"

ORDEN = ["ley_aduanera.json", "reglamento_la.json", "rgce.json", "reglas_se.json", "immex.json"]

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Normativa Aduanera Mexicana</title>
<style>
:root {
  --bg: #f7f6f3; --panel: #ffffff; --tinta: #1f2937; --sutil: #6b7280;
  --acento: #7a1f2b; --acento-suave: #f3e2e5; --borde: #e5e1d8; --hover: #efece5;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: Georgia, 'Times New Roman', serif; background: var(--bg); color: var(--tinta); }
header {
  background: var(--acento); color: #fff; padding: 10px 20px;
  display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap;
}
header h1 { font-size: 1.15rem; margin: 0; font-weight: normal; letter-spacing: .03em; }
header .meta { font-size: .75rem; opacity: .85; font-family: system-ui, sans-serif; }
#buscador {
  margin-left: auto; font-family: system-ui, sans-serif; font-size: .9rem;
  padding: 6px 12px; border: none; border-radius: 20px; width: 320px; max-width: 90vw;
}
.tabs { display: flex; gap: 4px; padding: 8px 20px 0; background: var(--panel); border-bottom: 1px solid var(--borde); overflow-x: auto; }
.tab {
  font-family: system-ui, sans-serif; font-size: .82rem; padding: 8px 14px; cursor: pointer;
  border: 1px solid var(--borde); border-bottom: none; border-radius: 8px 8px 0 0; background: var(--bg); white-space: nowrap;
}
.tab.activa { background: var(--panel); color: var(--acento); font-weight: 600; border-color: var(--acento); }
main { display: flex; height: calc(100vh - 96px); }
#indice {
  width: 360px; min-width: 250px; overflow-y: auto; background: var(--panel);
  border-right: 1px solid var(--borde); padding: 10px 0 40px; font-family: system-ui, sans-serif; font-size: .82rem;
}
#indice .titulo { padding: 8px 14px 2px; font-weight: 700; color: var(--acento); font-size: .8rem; }
#indice .titulo small { display: block; font-weight: 400; color: var(--sutil); }
#indice .capitulo { padding: 6px 14px 2px 22px; font-weight: 600; }
#indice .capitulo small { display: block; font-weight: 400; color: var(--sutil); }
#indice .seccion { padding: 4px 14px 2px 30px; font-style: italic; color: var(--sutil); }
#indice a.art {
  display: block; padding: 3px 14px 3px 38px; color: var(--tinta); text-decoration: none;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
#indice a.art:hover { background: var(--hover); }
#indice a.art.activo { background: var(--acento-suave); color: var(--acento); font-weight: 600; }
#indice a.art b { font-weight: 600; }
#contenido { flex: 1; overflow-y: auto; padding: 28px 48px 80px; }
.migas { font-family: system-ui, sans-serif; font-size: .75rem; color: var(--sutil); margin-bottom: 14px; }
article h2 { color: var(--acento); font-size: 1.3rem; margin: 0 0 2px; }
article h3.epigrafe { font-size: .95rem; color: var(--sutil); font-weight: 500; margin: 0 0 10px; font-style: italic; }
article .parrafo { margin: 0 0 .8em; line-height: 1.55; text-align: justify; }
article .fraccion { margin: 0 0 .6em 2.2em; text-indent: -1.2em; line-height: 1.5; text-align: justify; }
article pre.anexo {
  font-family: Consolas, monospace; font-size: .78rem; line-height: 1.45;
  background: var(--panel); border: 1px solid var(--borde); border-radius: 6px;
  padding: 14px; overflow-x: auto; white-space: pre-wrap;
}
.notas { margin-top: 22px; border-top: 1px dashed var(--borde); padding-top: 10px; }
.notas div { font-family: system-ui, sans-serif; font-size: .72rem; color: var(--sutil); margin: 2px 0; }
.refs { margin: 10px 0 20px; display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  font-family: system-ui, sans-serif; font-size: .72rem; background: var(--acento-suave); color: var(--acento);
  padding: 3px 10px; border-radius: 12px; cursor: pointer; border: 1px solid transparent;
}
.chip:hover { border-color: var(--acento); }
.chip.externa { background: #eee; color: var(--sutil); cursor: default; }
a.refint { color: var(--acento); text-decoration: underline dotted; cursor: pointer; }
details.historial { margin-top: 18px; font-family: system-ui, sans-serif; font-size: .8rem; }
details.historial summary { cursor: pointer; color: var(--acento); font-weight: 600; }
details.historial .anterior {
  margin-top: 8px; padding: 12px; background: #faf5ec; border-left: 3px solid var(--acento);
  font-family: Georgia, serif; font-size: .85rem; white-space: pre-wrap;
}
details.historial .fuente { color: var(--sutil); font-size: .72rem; margin-top: 4px; }
#resultados { padding: 10px 0; }
.resultado { padding: 10px 14px; border-bottom: 1px solid var(--borde); cursor: pointer; }
.resultado:hover { background: var(--hover); }
.resultado .de { font-family: system-ui, sans-serif; font-size: .72rem; color: var(--acento); font-weight: 600; }
.resultado .frag { font-size: .85rem; color: var(--tinta); }
.resultado mark { background: #f5d97e; }
.aviso { font-family: system-ui, sans-serif; color: var(--sutil); font-size: .85rem; padding: 20px; }
@media (max-width: 760px) { main { flex-direction: column; height: auto; } #indice { width: 100%; max-height: 40vh; } }
</style>
</head>
<body>
<header>
  <h1>Normativa Aduanera Mexicana</h1>
  <span class="meta" id="meta-header"></span>
  <input id="buscador" type="search" placeholder="Buscar artículo, regla o texto… (ej. 36-A, 1.5.1, pedimento)">
</header>
<div class="tabs" id="tabs"></div>
<main>
  <nav id="indice"></nav>
  <section id="contenido"><div class="aviso">Selecciona un artículo del índice o usa el buscador.</div></section>
</main>
<script id="datos" type="application/json">__DATOS__</script>
<script>
const DATOS = JSON.parse(document.getElementById('datos').textContent);
const ORDS = {};
DATOS.ordenamientos.forEach(o => ORDS[o.id] = o);
const IDX = {};
DATOS.ordenamientos.forEach(o => o.articulos.forEach(a => IDX[a.id] = {ord: o.id, art: a}));
let ordActual = DATOS.ordenamientos[0].id;

const NOMBRES_EXT = {CFF: 'Código Fiscal de la Federación', RMF: 'Resolución Miscelánea Fiscal',
  LIGIE: 'Ley de los Impuestos Generales de Importación y Exportación', LIVA: 'Ley del IVA',
  LIEPS: 'Ley del IEPS', LFD: 'Ley Federal de Derechos', LISR: 'Ley del ISR', LCE: 'Ley de Comercio Exterior',
  RLCE: 'Reglamento de la Ley de Comercio Exterior', CPEUM: 'Constitución', EXT: 'Otro ordenamiento'};

const norm = s => s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase();
const esReglas = o => o.tipo === 'reglas';

function pintaTabs() {
  const el = document.getElementById('tabs');
  el.innerHTML = '';
  DATOS.ordenamientos.forEach(o => {
    const t = document.createElement('div');
    t.className = 'tab' + (o.id === ordActual ? ' activa' : '');
    t.textContent = o.id === 'RCSE' ? 'Reglas SE' : (o.id === 'RGCE' ? 'RGCE 2026' : o.nombre);
    t.title = o.nombre + ' · Última reforma: ' + (o.ultima_reforma || o.publicacion_original || '');
    t.onclick = () => { ordActual = o.id; pintaTabs(); pintaIndice(); };
    el.appendChild(t);
  });
  const o = ORDS[ordActual];
  document.getElementById('meta-header').textContent =
    'Textos vigentes · generado ' + DATOS.generado + (o.ultima_reforma ? ' · últ. reforma ' + o.ultima_reforma : '');
}

function etiqueta(o, a) {
  if (a.numero.startsWith('Anexo')) return a.numero;
  return (esReglas(o) ? '' : 'Art. ') + a.numero;
}

function pintaIndice() {
  const el = document.getElementById('indice');
  el.innerHTML = '';
  const o = ORDS[ordActual];
  if (o.glosario) {
    const ln = document.createElement('a');
    ln.className = 'art'; ln.href = '#' + o.id + '-glosario';
    ln.innerHTML = '<b>Glosario</b>';
    el.appendChild(ln);
  }
  let t0 = null, c0 = null, s0 = null;
  o.articulos.forEach(a => {
    if (a.titulo && a.titulo !== t0) {
      t0 = a.titulo; c0 = s0 = null;
      const d = document.createElement('div'); d.className = 'titulo';
      d.innerHTML = 'Título ' + a.titulo + (a.titulo_nombre ? '<small>' + a.titulo_nombre + '</small>' : '');
      el.appendChild(d);
    }
    if (a.capitulo && a.capitulo !== c0) {
      c0 = a.capitulo; s0 = null;
      const d = document.createElement('div'); d.className = 'capitulo';
      const cap = a.capitulo === 'ANEXOS' ? 'Anexos' : 'Capítulo ' + a.capitulo;
      d.innerHTML = cap + (a.capitulo_nombre ? '<small>' + a.capitulo_nombre + '</small>' : '');
      el.appendChild(d);
    }
    if (a.seccion && a.seccion !== s0) {
      s0 = a.seccion;
      const d = document.createElement('div'); d.className = 'seccion';
      d.textContent = 'Sección ' + a.seccion + (a.seccion_nombre ? ' · ' + a.seccion_nombre : '');
      el.appendChild(d);
    }
    const ln = document.createElement('a');
    ln.className = 'art'; ln.id = 'idx-' + a.id; ln.href = '#' + a.id;
    const desc = a.epigrafe || a.texto.replace(/^[^\\n]{0,14}[\\.\\-]\\s*/, '').slice(0, 80);
    ln.innerHTML = '<b>' + etiqueta(o, a) + '</b> · ' + desc.slice(0, 80);
    el.appendChild(ln);
  });
  if (o.transitorios) {
    const ln = document.createElement('a');
    ln.className = 'art'; ln.href = '#' + o.id + '-transitorios';
    ln.innerHTML = '<b>Transitorios</b>';
    el.appendChild(ln);
  }
}

function linkifica(html, ordId) {
  html = html.replace(
    /(art[íi]culos?\\s+)((?:\\d+o?\\.?(?:-[A-Z])?(?:\\s+(?:bis|ter)(?:\\s+\\d+)?)?)(?:\\s*(?:,|y|o|e)\\s*(?:\\d+o?\\.?(?:-[A-Z])?(?:\\s+(?:bis|ter)(?:\\s+\\d+)?)?))*)([^;\\.]{0,90}?\\s+de(?:l)?\\s+(la\\s+Ley\\s+Aduanera|la\\s+Ley(?!\\s+(?:del?\\s|Federal|General))|esta\\s+Ley|este\\s+Reglamento|el\\s+Reglamento|presente\\s+Decreto|Decreto\\s+IMMEX))/gi,
    (m, pre, nums, resto) => {
      let dest = 'LA';
      if (/reglamento/i.test(resto)) dest = ordId === 'RCSE' ? 'RLCE' : 'RLA';
      else if (/decreto/i.test(resto)) dest = 'IMMEX';
      else if (/la\\s+ley(?!\\s+aduanera)/i.test(resto) && ordId === 'RCSE') dest = 'LCE';
      const numsLink = nums.replace(/\\d+o?\\.?(?:-[A-Z])?(?:\\s+(?:bis|ter)(?:\\s+\\d+)?)?/g, tok => {
        let clave = tok.trim().replace(/\\.$/, '');
        if (clave.endsWith('o')) clave = clave.slice(0, -1);
        if (/\\s/.test(clave)) clave = clave.toLowerCase().replace(/\\s+/g, '-');
        const destino = dest + '-' + clave;
        return IDX[destino] ? '<a class="refint" data-ir="' + destino + '">' + tok + '</a>' : tok;
      });
      return pre + numsLink + resto;
    });
  html = html.replace(/(reglas?\\s+)((?:\\d+\\.\\d+\\.\\d+\\.?)(?:\\s*(?:,|y|o)\\s*\\d+\\.\\d+\\.\\d+\\.?)*)/gi,
    (m, pre, nums) => {
      const dest = ordId === 'RCSE' ? 'RCSE' : 'RGCE';
      return pre + nums.replace(/\\d+\\.\\d+\\.\\d+/g, n =>
        IDX[dest + '-' + n] ? '<a class="refint" data-ir="' + dest + '-' + n + '">' + n + '</a>' : n);
    });
  html = html.replace(/Anexo\\s+(22|24)\\b(?!\\s*\\.)/g, (m, n) =>
    IDX['RGCE-anexo-' + n] ? '<a class="refint" data-ir="RGCE-anexo-' + n + '">' + m + '</a>' : m);
  return html;
}

function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }

function chipRef(r) {
  const destino = r.ord + '-' + r.art;
  if (IDX[destino]) {
    const et = r.art.startsWith('anexo-') ? r.ord + ' ' + r.art.replace('-', ' ') :
      (ORDS[r.ord] && esReglas(ORDS[r.ord]) ? r.ord + ' ' + r.art : r.ord + ' art. ' + r.art);
    return '<span class="chip" data-ir="' + destino + '">' + et + '</span>';
  }
  const nombre = NOMBRES_EXT[r.ord] || r.ord;
  const et = r.ord + (r.art ? ' ' + r.art : '');
  return '<span class="chip externa" title="' + esc(r.nombre || nombre) + ' — no integrado al visor">' + et + '</span>';
}

function muestraArticulo(id) {
  const e = IDX[id];
  if (!e) return;
  ordActual = e.ord; pintaTabs(); pintaIndice();
  const o = ORDS[e.ord], a = e.art;
  const migas = [o.nombre,
    a.titulo ? 'Título ' + a.titulo + (a.titulo_nombre ? ' — ' + a.titulo_nombre : '') : null,
    a.capitulo ? (a.capitulo === 'ANEXOS' ? 'Anexos' : 'Capítulo ' + a.capitulo) + (a.capitulo_nombre ? ' — ' + a.capitulo_nombre : '') : null,
    a.seccion ? 'Sección ' + a.seccion + (a.seccion_nombre ? ' — ' + a.seccion_nombre : '') : null
  ].filter(Boolean).join(' › ');
  let cuerpo;
  if (a.formato === 'pre') {
    cuerpo = '<pre class="anexo">' + esc(a.texto) + '</pre>';
  } else {
    cuerpo = a.texto.split('\\n').map(p => {
      if (!p.trim()) return '';
      const cls = /^[IVXL]+[\\.\\)]|^[a-z]\\)|^\\d+\\)/.test(p.trim()) ? 'fraccion' : 'parrafo';
      return '<p class="' + cls + '">' + linkifica(esc(p), e.ord) + '</p>';
    }).join('');
  }
  const refs = (a.referencias || []).map(chipRef).join('');
  const notas = a.notas_reforma && a.notas_reforma.length
    ? '<div class="notas">' + a.notas_reforma.map(n => '<div>' + esc(n) + '</div>').join('') + '</div>' : '';
  const hist = (a.historial || []).map(h =>
    '<details class="historial"><summary>Texto anterior (vigente hasta ' + h.vigente_hasta + ')</summary>' +
    '<div class="anterior">' + esc(h.texto) + '</div>' +
    '<div class="fuente">' + esc(h.fuente_anterior || '') + (h.motivo ? ' · ' + esc(h.motivo) : '') + '</div></details>').join('');
  const titulo = a.numero.startsWith('Anexo') ? a.numero : (esReglas(o) ? 'Regla ' + a.numero : 'Artículo ' + a.numero);
  document.getElementById('contenido').innerHTML =
    '<div class="migas">' + migas + '</div>' +
    '<article><h2>' + titulo + '</h2>' +
    (a.epigrafe ? '<h3 class="epigrafe">' + esc(a.epigrafe) + '</h3>' : '') +
    (refs ? '<div class="refs">' + refs + '</div>' : '') +
    cuerpo + notas + hist + '</article>';
  document.getElementById('contenido').scrollTop = 0;
  document.querySelectorAll('#indice a.art').forEach(x => x.classList.remove('activo'));
  const ix = document.getElementById('idx-' + id);
  if (ix) { ix.classList.add('activo'); ix.scrollIntoView({block: 'nearest'}); }
}

function muestraBloque(ordId, campo, titulo) {
  const o = ORDS[ordId];
  ordActual = ordId; pintaTabs(); pintaIndice();
  document.getElementById('contenido').innerHTML =
    '<div class="migas">' + o.nombre + ' › ' + titulo + '</div><article><h2>' + titulo + '</h2>' +
    o[campo].split('\\n').map(p => p.trim() ? '<p class="parrafo">' + esc(p) + '</p>' : '').join('') +
    '</article>';
  document.getElementById('contenido').scrollTop = 0;
}

function busca(q) {
  const cont = document.getElementById('contenido');
  if (!q || q.length < 2) { return; }
  const nq = norm(q);
  const res = [];
  DATOS.ordenamientos.forEach(o => o.articulos.forEach(a => {
    if (res.length > 400) return;
    const esNum = norm('' + a.numero).startsWith(nq) || norm(a.numero.replace('o','')) === nq;
    const enEpigrafe = a.epigrafe && norm(a.epigrafe).indexOf(nq) >= 0;
    const pos = norm(a.texto).indexOf(nq);
    if (esNum || enEpigrafe || pos >= 0) res.push({o, a, pos: esNum ? 0 : Math.max(pos, 0), esNum});
  }));
  res.sort((x, y) => (y.esNum - x.esNum));
  cont.innerHTML = '<div class="aviso">' + res.length + ' resultados para «' + esc(q) + '»</div><div id="resultados">' +
    res.slice(0, 150).map(r => {
      const ini = Math.max(0, r.pos - 60);
      let frag = esc(r.a.texto.slice(ini, ini + 220));
      if (!r.esNum) {
        const re = new RegExp(q.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'), 'i');
        frag = frag.replace(re, m => '<mark>' + m + '</mark>');
      }
      return '<div class="resultado" data-ir="' + r.a.id + '"><div class="de">' + r.o.nombre + ' — ' + etiqueta(r.o, r.a) +
        (r.a.epigrafe ? ' · ' + esc(r.a.epigrafe.slice(0, 60)) : '') +
        '</div><div class="frag">…' + frag + '…</div></div>';
    }).join('') + '</div>';
}

document.addEventListener('click', ev => {
  const t = ev.target.closest('[data-ir]');
  if (t) { ev.preventDefault(); location.hash = t.dataset.ir; }
});
document.getElementById('buscador').addEventListener('input', ev => busca(ev.target.value));
window.addEventListener('hashchange', () => enruta());
function enruta() {
  const h = decodeURIComponent(location.hash.slice(1));
  if (!h) return;
  if (h.endsWith('-transitorios')) { muestraBloque(h.replace('-transitorios',''), 'transitorios', 'Transitorios'); return; }
  if (h.endsWith('-glosario')) { muestraBloque(h.replace('-glosario',''), 'glosario', 'Glosario'); return; }
  muestraArticulo(h);
}
pintaTabs(); pintaIndice(); enruta();
</script>
</body>
</html>
"""


def main():
    ordenamientos = []
    for nombre in ORDEN:
        f = DATA / nombre
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            d.pop("material_posterior", None)  # no se muestra; reduce peso
            ordenamientos.append(d)
    paquete = {"generado": date.today().isoformat(), "ordenamientos": ordenamientos}
    datos = json.dumps(paquete, ensure_ascii=False).replace("</", "<\\/")
    SALIDA.write_text(PLANTILLA.replace("__DATOS__", datos), encoding="utf-8")
    kb = SALIDA.stat().st_size // 1024
    total = sum(len(o["articulos"]) for o in ordenamientos)
    print(f"normativa.html generado ({kb} KB, {len(ordenamientos)} ordenamientos, {total} entradas)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
