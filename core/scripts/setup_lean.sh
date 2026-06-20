#!/bin/bash
set -e

echo "=== 1. Verificando gestor de versiones de Lean (elan) ==="
if ! command -v elan &> /dev/null; then
    echo "Instalando elan..."
    curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
    source $HOME/.elan/env
else
    echo "elan ya está instalado."
fi

echo "=== 2. Configurando entorno del proyecto ==="
cd mathematics/leanlib/

echo "=== 3. Descargando dependencias (Mathlib4) ==="
lake update

echo "=== 4. Obteniendo binarios precompilados de Mathlib (Caché) ==="
lake exe cache get

echo "=== 5. Compilando QuantumAlgebra ==="
lake build

echo "=== Entorno Lean 4 listo y compilado ==="
