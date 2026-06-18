"""Quick dependency check script."""
import sys

deps = {
    "fastapi": False,
    "uvicorn": False,
    "pydantic": False,
    "dotenv": False,
    "numpy": False,
    "httpx": False,
    "yaml": False,
    "sklearn": False,
    "faiss": False,
    "sentence_transformers": False,
    "torch": False,
}

for mod in deps:
    try:
        __import__(mod)
        deps[mod] = True
    except ImportError:
        pass

print(f"Python: {sys.version}")
print()
for mod, ok in deps.items():
    status = "OK" if ok else "MISSING"
    print(f"  {mod:25s} {status}")

missing = [m for m, ok in deps.items() if not ok]
if missing:
    print(f"\nMissing: {', '.join(missing)}")
else:
    print("\nAll dependencies installed.")
