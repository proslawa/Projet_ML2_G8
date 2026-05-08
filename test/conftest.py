import sys
from pathlib import Path

# Garantit que src/ est dans sys.path pour tous les tests, local et CI
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
