"""
Netlify function entrypoint for the FastAPI backend.
"""

import sys
import os

_here = os.path.dirname(os.path.abspath(__file__))
print(f"[api] _here={_here} cwd={os.getcwd()}")

# Resolve apps/ directory — two possible layouts in Lambda:
# 1. netlify/functions/api.py → ../../apps
# 2. api.py at Lambda root   → ./apps
for _rel in (os.path.join("..", "..", "apps"), "apps"):
    _p = os.path.normpath(os.path.join(_here, _rel))
    if os.path.isdir(os.path.join(_p, "backend")):
        sys.path.insert(0, _p)
        print(f"[api] sys.path → {_p}")
        break
else:
    print(f"[api] ERROR: apps/backend not found. _here={_here}")
    print(f"[api] contents: {os.listdir(_here)[:30]}")

try:
    from mangum import Mangum
    from backend.api.main import app
    print("[api] import OK")
    _mangum = Mangum(app, lifespan="off")
except Exception as exc:
    import traceback
    print(f"[api] import FAILED: {exc}")
    traceback.print_exc()
    _mangum = None


def handler(event, context):
    if _mangum is None:
        return {
            "statusCode": 500,
            "body": '{"detail":"Backend failed to load"}',
            "headers": {"Content-Type": "application/json"},
        }
    return _mangum(event, context)
