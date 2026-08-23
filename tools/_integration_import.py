"""Import integration modules from standalone tools.

The integration package's ``__init__.py`` imports Home Assistant, which is not
installed in a plain tooling environment. These modules are pure Python though,
so they are loaded directly from their files under a synthetic package name -
that keeps the ``from .firmware_templates import ...`` relative imports working
without ever executing the package ``__init__``.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

_PACKAGE = "bauergroup_hargassnerintegration"
_PACKAGE_DIR = Path(__file__).resolve().parent.parent / "custom_components" / _PACKAGE


def load_module(name: str) -> Any:
    """Load a single module from the integration package by file name.

    Args:
        name: Module name without the ``.py`` suffix (e.g. ``message_parser``)

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the integration package or module is missing.
    """
    if _PACKAGE not in sys.modules:
        if not _PACKAGE_DIR.is_dir():
            raise FileNotFoundError(f"Integration package not found: {_PACKAGE_DIR}")
        package = types.ModuleType(_PACKAGE)
        package.__path__ = [str(_PACKAGE_DIR)]
        sys.modules[_PACKAGE] = package

    qualified = f"{_PACKAGE}.{name}"
    if qualified in sys.modules:
        return sys.modules[qualified]

    path = _PACKAGE_DIR / f"{name}.py"
    if not path.is_file():
        raise FileNotFoundError(f"Module not found: {path}")

    spec = importlib.util.spec_from_file_location(qualified, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[qualified] = module
    spec.loader.exec_module(module)
    return module
