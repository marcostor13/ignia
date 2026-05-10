"""
Netlify function entrypoint for the FastAPI backend.

Mangum wraps the ASGI app so it can be invoked by Netlify's Lambda runtime.
lifespan="off" is required because Netlify functions don't support lifespan events.
"""

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))

# Try both possible paths:
# - "../../apps"  works when Netlify preserves dir structure (netlify/functions/api.py)
# - "apps"        works when Netlify strips the prefix (api.py at Lambda root)
for _rel in (os.path.join("..", "..", "apps"), "apps"):
    _p = os.path.normpath(os.path.join(_here, _rel))
    if os.path.isdir(os.path.join(_p, "backend")):
        sys.path.insert(0, _p)
        break

from mangum import Mangum
from backend.api.main import app

handler = Mangum(app, lifespan="off")
