#!/bin/bash
# Copyright © 2026 Alex Felizardo. Licença MIT: ver LICENSE.
# Gera dist/Udjath.app (+ dist/Udjath-<versão>.zip) com o py2app. Cria a venv se faltar.
#
# Variáveis opcionais:
#   VERSION=1.0.0
#   SIGN_IDENTITY="Developer ID Application: …"   (por omissão: "ad hoc")
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
[ -f "$ROOT/setup.py" ] || { echo "setup.py não encontrado em $ROOT"; exit 1; }

VERSION="${VERSION:-0.1.0}"
SIGN_IDENTITY="${SIGN_IDENTITY:--}"
APP="dist/Udjath.app"
ZIP="dist/Udjath-$VERSION.zip"

echo "==> 1/4 Ambiente"
if [ ! -x venv/bin/python3 ]; then
  python3 -m venv venv
  ./venv/bin/pip install -q -r requirements.txt
fi

echo "==> 2/4 Compilar $APP (versão $VERSION)"
rm -rf "$ROOT/build" "$ROOT/dist"
VERSION="$VERSION" ./venv/bin/python3 setup.py py2app >/dev/null
[ -d "$APP" ] || { echo "$APP não foi gerado"; exit 1; }
cp LICENSE TRADEMARKS.md "$APP/Contents/Resources/"

echo "==> 3/4 Assinar ($SIGN_IDENTITY)"
codesign --force --deep --sign "$SIGN_IDENTITY" "$APP"
codesign --verify --deep --strict "$APP"

echo "==> 4/4 Comprimir"
ditto -c -k --keepParent "$APP" "$ZIP"
echo "$ZIP"
echo "SHA-256 do zip: $(shasum -a 256 "$ZIP" | cut -d' ' -f1)"
