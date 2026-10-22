# -*- coding: utf-8 -*-
"""Corre el pipeline completo en el orden obligatorio y luego scripts/verificar.py.
Se detiene en el primer paso que falle (un ancla no encontrada truena a propósito).

Uso: python scripts/actualizar.py [--base REF]   (REF de git contra la que verificar; por omisión HEAD)
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
PASOS = [
    "parse_ordenamiento.py",        # LA y RLA (LeyesBiblio)
    "parse_rgce.py",                # RGCE base DOF
    "parse_anexos.py",              # Anexos 1, 2, 22, 24, 30
    "aplicar_modificaciones.py",    # resoluciones de modificaciones RGCE, con historial
    "parse_se.py",                  # Reglas SE (compilado SNICE)
    "aplicar_modificaciones_se.py", # Acuerdos SE posteriores al compilado, con historial
    "parse_immex.py",               # Decreto IMMEX (compilado SNICE)
    "extraer_referencias.py",
    "generar_indice.py",
    "build_html.py",
]


def main():
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else "HEAD"
    for paso in PASOS:
        print(f"== {paso}", flush=True)
        r = subprocess.run([sys.executable, "-I", str(SCRIPTS / paso)])
        if r.returncode:
            print(f"FALLÓ {paso} (código {r.returncode}); no se siguió con el pipeline.")
            return r.returncode
    print("== verificar.py", flush=True)
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "verificar.py"), "--base", base]).returncode


if __name__ == "__main__":
    sys.exit(main())
