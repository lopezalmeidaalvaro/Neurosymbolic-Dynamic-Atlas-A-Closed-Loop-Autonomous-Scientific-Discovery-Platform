import Lake
open Lake DSL

package «Mathematics» where
  -- Configuración base

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.8.0"

@[default_target]
lean_lib «QuantumAlgebra» where
  -- Configuración de la librería
