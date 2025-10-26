#!/usr/bin/env bash
set -e

# === CONFIG ===
VENV_DIR="../venv"
LIBOQS_DIR="liboqs"
PYOQS_DIR="liboqs-python"

# === ENV SETUP ===
echo "[*] Creating Python virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

echo "[*] Installing build dependencies..."
sudo apt update
sudo apt install -y cmake gcc g++ ninja-build python3-dev git libssl-dev

# === BUILD liboqs ===
echo "[*] Cloning and building liboqs..."
git clone --depth=1 --recursive https://github.com/open-quantum-safe/liboqs.git $LIBOQS_DIR
cd $LIBOQS_DIR
mkdir build && cd build
cmake -GNinja -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=../install ..
ninja install
cd ../..
export LD_LIBRARY_PATH="$PWD/$LIBOQS_DIR/install/lib:$LD_LIBRARY_PATH"
export CMAKE_PREFIX_PATH="$PWD/$LIBOQS_DIR/install"

# === BUILD liboqs-python ===
echo "[*] Cloning and building liboqs-python..."
git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python.git $PYOQS_DIR
cd $PYOQS_DIR
pip install -U pip setuptools wheel
pip install numpy cffi
python setup.py build_ext --library-dirs=$PWD/../$LIBOQS_DIR/install/lib --include-dirs=$PWD/../$LIBOQS_DIR/install/include
python setup.py install
cd ..

# === TEST ===
echo "[*] Testing installation..."
python - <<'EOF'
import oqs
print("Available PQ Signatures:", oqs.get_enabled_sig_mechanisms())
EOF

echo "[+] Done! Activate your env with:"
echo "    source $VENV_DIR/bin/activate"
