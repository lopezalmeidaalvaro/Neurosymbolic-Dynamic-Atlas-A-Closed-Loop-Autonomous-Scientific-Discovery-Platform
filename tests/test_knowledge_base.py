import sys
import sqlite3
import tempfile
from pathlib import Path
from contextlib import closing
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mathematics.knowledge_base.library_manager import FormalKnowledgeBase


@pytest.fixture
def temp_db():
    """Fixture providing a temporary FormalKnowledgeBase instance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_knowledge.db"
        kb = FormalKnowledgeBase(db_path=db_file)
        yield kb


def test_kb_tables_exist(temp_db):
    """Verify that tables are created automatically on initialization."""
    with closing(temp_db._connect()) as conn:
        cursor = conn.cursor()

        # Check theorems table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='theorems';"
        )
        assert cursor.fetchone() is not None

        # Check theorem_dependencies table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='theorem_dependencies';"
        )
        assert cursor.fetchone() is not None


def test_add_and_get_theorem(temp_db):
    """Verify storing a theorem computes SHA-256 and retrieves correctly."""
    lean_proof = "intro h\nexact h"
    temp_db.add_theorem(
        theorem_id="identity_thm",
        domain="mathematics",
        schema_version="1.0",
        statement="P -> P",
        lean_proof=lean_proof,
        verified=True,
        provenance="DETERMINISTIC_RULE",
        dependencies=["axiom_1", "axiom_2"],
    )

    thm = temp_db.get_theorem("identity_thm")
    assert thm is not None
    assert thm["id"] == "identity_thm"
    assert thm["domain"] == "mathematics"
    assert thm["schema_version"] == "1.0"
    assert thm["statement"] == "P -> P"
    assert thm["lean_proof"] == lean_proof
    assert thm["verified"] is True
    assert thm["provenance"] == "DETERMINISTIC_RULE"
    assert "dependencies" in thm
    assert set(thm["dependencies"]) == {"axiom_1", "axiom_2"}

    # Validate SHA-256 hash
    import hashlib

    expected_hash = hashlib.sha256(lean_proof.encode("utf-8")).hexdigest()
    assert thm["proof_hash"] == expected_hash


def test_duplicate_theorem_raises_error(temp_db):
    """Verify duplicate primary key raises sqlite3.IntegrityError."""
    temp_db.add_theorem(
        theorem_id="thm_a",
        domain="physics",
        schema_version="1.0",
        statement="x = y",
        lean_proof="rfl",
        verified=True,
        provenance="AUTO_FORMALIZED",
    )

    with pytest.raises(sqlite3.IntegrityError):
        temp_db.add_theorem(
            theorem_id="thm_a",  # Duplicate ID
            domain="quantum",
            schema_version="1.0",
            statement="z = w",
            lean_proof="rfl",
            verified=False,
            provenance="DETERMINISTIC_RULE",
        )


def test_get_dependents(temp_db):
    """Verify get_dependents maps dependency graph correctly."""
    temp_db.add_theorem(
        theorem_id="lemma_1",
        domain="mathematics",
        schema_version="1.0",
        statement="statement 1",
        lean_proof="proof 1",
        verified=True,
        provenance="DETERMINISTIC_RULE",
    )

    temp_db.add_theorem(
        theorem_id="theorem_2",
        domain="mathematics",
        schema_version="1.0",
        statement="statement 2",
        lean_proof="proof 2",
        verified=True,
        provenance="AUTO_FORMALIZED",
        dependencies=["lemma_1", "other_ref"],
    )

    temp_db.add_theorem(
        theorem_id="theorem_3",
        domain="mathematics",
        schema_version="1.0",
        statement="statement 3",
        lean_proof="proof 3",
        verified=True,
        provenance="DETERMINISTIC_RULE",
        dependencies=["lemma_1"],
    )

    dependents = temp_db.get_dependents("lemma_1")
    assert set(dependents) == {"theorem_2", "theorem_3"}


def test_cascade_delete(temp_db):
    """Verify ON DELETE CASCADE removes dependencies from dependency table."""
    temp_db.add_theorem(
        theorem_id="thm_parent",
        domain="mathematics",
        schema_version="1.0",
        statement="parent stmt",
        lean_proof="proof",
        verified=True,
        provenance="DETERMINISTIC_RULE",
        dependencies=["dep_a", "dep_b"],
    )

    # Confirm dependency rows exist
    with closing(temp_db._connect()) as conn:
        rows = conn.execute(
            "SELECT count(*) as count FROM theorem_dependencies WHERE theorem_id = ?",
            ("thm_parent",),
        ).fetchone()
        assert rows["count"] == 2

    # Delete theorem from parent table
    with closing(temp_db._connect()) as conn:
        with conn:
            conn.execute("DELETE FROM theorems WHERE id = ?", ("thm_parent",))

    # Confirm dependency rows are deleted automatically in cascade
    with closing(temp_db._connect()) as conn:
        rows = conn.execute(
            "SELECT count(*) as count FROM theorem_dependencies WHERE theorem_id = ?",
            ("thm_parent",),
        ).fetchone()
        assert rows["count"] == 0
