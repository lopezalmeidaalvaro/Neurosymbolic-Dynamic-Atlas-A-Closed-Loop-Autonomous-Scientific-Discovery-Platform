from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _fixed_seed():
    from neurosymbolic.reproducibility import set_global_seed

    set_global_seed(123)
