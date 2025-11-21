#!/bin/bash
set -e

# -------------------------
# Configuration
# -------------------------
ICON=scxctl_gui.png

# Function to build a specific flavor
build_flavor() {
    FLAVOR=$1
    PYFILE=$2
    APP_NAME="scxctl_gui_${FLAVOR}"
    APPDIR="AppDir_${FLAVOR}"

    echo "========================================"
    echo "🚀 Building $FLAVOR version ($PYFILE)..."
    echo "========================================"

    # Cleanup specific to this build
    rm -rf "build/$APP_NAME" "dist/$APP_NAME" "$APPDIR" "${APP_NAME}"*.AppImage "$APP_NAME.spec"

    if [ "$FLAVOR" == "gtk" ]; then
        echo "🔹 Building GTK version (script-based, no PyInstaller)..."
        
        # For GTK, we create a simple wrapper that uses system Python
        mkdir -p "$APPDIR/usr/bin"
        
        # Copy the Python script directly
        cp "$PYFILE" "$APPDIR/usr/bin/$APP_NAME.py"
        
        # Create a launcher script
        cat > "$APPDIR/usr/bin/$APP_NAME" <<'EOFGTK'
#!/bin/bash
# GTK AppImage launcher - uses system Python with gi
SCRIPT_DIR="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
exec python3 "$SCRIPT_DIR/scxctl_gui_gtk.py" "$@"
EOFGTK
        chmod +x "$APPDIR/usr/bin/$APP_NAME"
        
    else
        # Qt version uses PyInstaller as before
        echo "🔹 Compiling Qt version with PyInstaller..."
        pyinstaller --noconsole --onedir --name "$APP_NAME" "$PYFILE"
        
        echo "🔹 Creating $APPDIR..."
        mkdir -p "$APPDIR/usr/bin"
        cp -r "dist/$APP_NAME/"* "$APPDIR/usr/bin/"
        chmod +x "$APPDIR/usr/bin/$APP_NAME"
    fi

    # 3️⃣ .desktop file
    echo "🔹 Creating .desktop file..."
    cat > "$APPDIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Name=SCXCTL GUI ($FLAVOR)
Exec=$APP_NAME
Icon=scxctl_gui
Type=Application
Categories=Utility;
EOF

    # 4️⃣ Icon
    if [ -f "$ICON" ]; then
        cp "$ICON" "$APPDIR/scxctl_gui.png"
    fi

    # 5️⃣ AppRun
    echo "🔹 Creating AppRun..."
    if [ "$FLAVOR" == "qt" ]; then
        cat > "$APPDIR/AppRun" <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
# Suppress system GIO module loading to avoid glib version mismatch warnings
export GIO_MODULE_DIR=""
exec "\$HERE/usr/bin/$APP_NAME" "\$@"
EOF
    else
        cat > "$APPDIR/AppRun" <<EOF
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
exec "\$HERE/usr/bin/$APP_NAME" "\$@"
EOF
    fi
    chmod +x "$APPDIR/AppRun"

    # 6️⃣ AppImageTool
    if [ ! -f appimagetool ]; then
        echo "🔹 Downloading appimagetool..."
        wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage -O appimagetool
        chmod +x appimagetool
    fi

    # 7️⃣ Generate AppImage
    echo "🔹 Generating AppImage..."
    # Use ARCH=x86_64 to avoid guessing issues if needed, or let it detect
    ./appimagetool "$APPDIR"

    echo "✅ ${APP_NAME} AppImage generated successfully!"
}

# Main logic
if [ "$1" == "qt" ]; then
    build_flavor "qt" "scxctl_gui_qt.py"
elif [ "$1" == "gtk" ]; then
    build_flavor "gtk" "scxctl_gui_gtk.py"
else
    echo "ℹ️  No argument provided. Building BOTH versions."
    echo "   Usage: ./build.sh [qt|gtk]"
    echo ""
    build_flavor "qt" "scxctl_gui_qt.py"
    build_flavor "gtk" "scxctl_gui_gtk.py"
fi
