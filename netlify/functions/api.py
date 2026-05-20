"""
Netlify function entrypoint for the FastAPI backend.
"""

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
print(f"[api] __file__={__file__} _here={_here}")
print(f"[api] cwd={os.getcwd()}")
print(f"[api] listdir(_here)={os.listdir(_here)[:20]}")

# Try both possible paths:
# - "../../apps"  works when Netlify preserves dir structure (netlify/functions/api.py)
# - "apps"        works when Netlify strips the prefix (api.py at Lambda root)
_resolved = False
for _rel in (os.path.join("..", "..", "apps"), "apps"):
    _p = os.path.normpath(os.path.join(_here, _rel))
    if os.path.isdir(os.path.join(_p, "backend")):
        sys.path.insert(0, _p)
        print(f"[api] sys.path inserted: {_p}")
        _resolved = True
        break

if not _resolved:
    print(f"[api] ERROR: could not find apps/backend. Searched: {_here}")

from mangum import Mangum
from backend.api.main import app

print("[api] FastAPI app loaded OK")
handler = Mangum(app, lifespan="off")
