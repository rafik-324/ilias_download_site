"""Erzeugt Einmalcodes für den Download der ILIAS Sync App.

Aufruf: python3 make_codes.py [ANZAHL]

* codes.txt: nur die Codes, einer pro Zeile. Bleibt lokal, nie ins Repo
* insert_codes.sql: nur SHA-256 Hashes, zum Einspielen in die Tabelle download_codes
Vorhandene Codes in codes.txt bleiben erhalten, neue werden angehängt.
"""

import argparse
import hashlib
import secrets
from pathlib import Path

# Ohne 0, O, 1, I, damit nichts verwechselt wird: 32 Zeichen, 8 Stellen = 40 Bit
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
HERE = Path(__file__).resolve().parent
TXT_PATH = HERE / "codes.txt"
SQL_PATH = HERE / "insert_codes.sql"


def new_code() -> str:
    raw = "".join(secrets.choice(ALPHABET) for _ in range(8))
    return "-".join(raw[i : i + 4] for i in range(0, 8, 4))


def code_hash(code: str) -> str:
    # Muss zur Edge Function passen: Großbuchstaben, Format XXXX-XXXX, SHA-256 hex
    return hashlib.sha256(code.upper().encode("ascii")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("anzahl", type=int, nargs="?", default=50)
    args = parser.parse_args()

    codes = TXT_PATH.read_text(encoding="utf-8").split() if TXT_PATH.exists() else []
    known = set(codes)

    new = []
    while len(new) < args.anzahl:
        code = new_code()
        if code not in known:
            known.add(code)
            new.append(code)

    codes += new
    TXT_PATH.write_text("\n".join(codes) + "\n", encoding="utf-8")
    TXT_PATH.chmod(0o600)

    # Immer alle Codes, schon vorhandene überspringt die Datenbank (on conflict)
    values = ",\n".join(f"  ('{code_hash(c)}', 'Code {i:02d}')" for i, c in enumerate(codes, 1))
    SQL_PATH.write_text(
        "insert into public.download_codes (code_hash, label) values\n"
        f"{values}\non conflict (code_hash) do nothing;\n",
        encoding="utf-8",
    )
    print(f"{len(new)} neue Codes, insgesamt {len(codes)}: {TXT_PATH.name}, {SQL_PATH.name}")


if __name__ == "__main__":
    main()
