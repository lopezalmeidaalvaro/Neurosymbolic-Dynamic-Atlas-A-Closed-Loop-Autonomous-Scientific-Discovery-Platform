import json
from pathlib import Path
from mathematics.ir_core.quantum_ir import QuantumEquivalenceIR
from mathematics.ir_core.physics_ir import PhysicsLawIR
from mathematics.ir_core.proof_ir import ProofGoalIR


def load_and_validate_quantum_ir(filepath: str | Path) -> QuantumEquivalenceIR:
    """Loads a JSON file and validates it against the QuantumEquivalenceIR schema.

    Raises ValidationError if validation fails.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return QuantumEquivalenceIR.model_validate(data)


def load_and_validate_physics_ir(filepath: str | Path) -> PhysicsLawIR:
    """Loads a JSON file and validates it against the PhysicsLawIR schema.

    Raises ValidationError if validation fails.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return PhysicsLawIR.model_validate(data)


def load_and_validate_proof_ir(filepath: str | Path) -> ProofGoalIR:
    """Loads a JSON file and validates it against the ProofGoalIR schema.

    Raises ValidationError if validation fails.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ProofGoalIR.model_validate(data)


if __name__ == "__main__":
    # Define schemas output directory relative to this file
    current_dir = Path(__file__).resolve().parent
    schemas_dir = current_dir / "schemas"
    schemas_dir.mkdir(parents=True, exist_ok=True)

    # Generate and dump Pydantic JSON schemas
    schema_mappings = {
        "quantum_equivalence_ir.schema.json": QuantumEquivalenceIR,
        "physics_law_ir.schema.json": PhysicsLawIR,
        "proof_goal_ir.schema.json": ProofGoalIR,
    }

    for filename, model in schema_mappings.items():
        schema_path = schemas_dir / filename
        schema_data = model.model_json_schema()
        with open(schema_path, "w", encoding="utf-8") as f:
            json.dump(schema_data, f, indent=2, ensure_ascii=False)
        print(f"Generated schema: {schema_path}")
