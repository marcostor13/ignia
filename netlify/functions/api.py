"""
Netlify function entrypoint for the FastAPI backend.

Mangum wraps the ASGI app so it can be invoked by Netlify's Lambda runtime.
lifespan="off" is required because Netlify functions don't support lifespan events.
"""

import sys
import os

# Ensure the backend package is importable from the Netlify function context
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/backend"))

from mangum import Mangum
from api.main import app

handler = Mangum(app, lifespan="off")
