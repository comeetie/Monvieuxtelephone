#!/usr/bin/env python3
import os
import subprocess
import sys

# Détermination du chemin absolu du dossier où se trouve ce script (./Stories/1)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemin vers ton script principal ../../prochain_passage.py
SCRIPT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "prochain_passage.py"))

# Arguments IDFM de ton choix :
STOP_ID = "stop_area:IDFM:68653"      # Exemple arrêt Coupvray

def main():
    # Lancement du script en sous-processus
    try:
        subprocess.run(
            ["python3", SCRIPT_PATH, STOP_ID],
            check=True
        )
    except Exception as e:
        print(f"[ERROR] Impossible d'exécuter prochain_passage.py : {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
