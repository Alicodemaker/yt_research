import sys
from pathlib import Path

# The scripts are standalone files, not a package: put their folder on the path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "yt-research" / "scripts"))
