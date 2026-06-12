-- Base definitions and axioms for quantum gates in Lean 4.
-- Namespace for isolating definitions.

namespace QuantumGates

axiom Gate : Type

axiom I : Gate
axiom H : Gate
axiom X : Gate
axiom Y : Gate
axiom Z : Gate
axiom CNOT : Gate
axiom SWAP : Gate

axiom compose : Gate → Gate → Gate

-- Composition operator notation (bullet)
local infixl:70 " ⬝ " => compose

-- Axiom stub for double Hadamard equivalence
axiom H_squared : H ⬝ H = I

end QuantumGates
