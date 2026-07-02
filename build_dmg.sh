#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv"
DIST="$ROOT/dist"
STAGING="$ROOT/build/dmg-staging"
DMG_NAME="Loader-1.9.dmg"
DATA_DIR="$STAGING/Loader"

cd "$ROOT"

if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install PyQt6 pylink-square pyinstaller
fi

"$VENV/bin/pip" install -q PyQt6 pylink-square pyinstaller

rm -rf "$ROOT/build" "$DIST" "$STAGING"
"$VENV/bin/pyinstaller" --noconfirm Loader.spec

mkdir -p "$STAGING" "$DATA_DIR"
cp -R "$DIST/Loader.app" "$STAGING/"
mkdir -p "$DATA_DIR/gui" "$DATA_DIR/config" "$DATA_DIR/files"
cp "$ROOT/gui/loader_win.ui" "$DATA_DIR/gui/"
if [[ -f "$ROOT/config/config.pckl" ]]; then
  cp "$ROOT/config/config.pckl" "$DATA_DIR/config/"
fi
cp -R "$ROOT/files/." "$DATA_DIR/files/"

cat > "$STAGING/Install Loader Data.command" <<'EOF'
#!/bin/bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/Loader"
DEST="/Users/Shared/Loader"
mkdir -p "$DEST"
ditto "$SRC" "$DEST"
echo "Loader data installed to $DEST"
echo "Press Enter to close."
read -r
EOF
chmod +x "$STAGING/Install Loader Data.command"

cat > "$STAGING/README.txt" <<'EOF'
Microbot Medical Loader 1.9

1. Drag Loader.app to Applications.
2. Double-click "Install Loader Data.command" to copy firmware/config data to /Users/Shared/Loader.
3. Launch Loader from Applications.
EOF

hdiutil create \
  -volname "Microbot Loader" \
  -srcfolder "$STAGING" \
  -ov \
  -format UDZO \
  "$DIST/$DMG_NAME"

echo "Created $DIST/$DMG_NAME"
