# Temporary compatibility shim for the Tower Actions proof workflow.
# Python imports sitecustomize automatically when the repository root is on sys.path.
# This exists only to satisfy the inline workflow assertion block that references
# Path without importing it; it will be removed after the proof run succeeds.
import builtins
from pathlib import Path
builtins.Path = Path
