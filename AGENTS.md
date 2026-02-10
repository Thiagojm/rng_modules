# Agent Guidelines for rng-modules

## Project Overview
Hardware and software random number generator modules for Python. Supports BitBabbler, TrueRNG hardware devices, plus software fallback using `secrets` module.

## Build/Test Commands

```bash
# Install dependencies
uv sync

# Run Python script
uv run python main.py

# Run tests with pytest
uv run pytest

# Run a specific test
uv run pytest tests/rng_devices/test_pseudo.py

# Run tests in parallel
uv run pytest -x

# Run a specific test script directly
uv run python tests/rng_devices/test_pseudo.py
uv run python rng_devices/test_bit.py
uv run python rng_devices/test_true.py

# Install additional dependencies
uv add <package>

# Update dependencies
uv lock
```

**Note:** Tests use pytest with asyncio support. Standalone test scripts are also available for direct execution.

## Code Style Guidelines

### Python Version
- **Python 3.13+** required

### Imports
- Group imports: stdlib → third-party → local
- Example:
  ```python
  import os
  import time
  from typing import Optional

  from serial.tools import list_ports
  import serial

  from .ftdi import FTDIDevice
  ```
- Use `from . import module` for relative imports within packages

### Formatting
- 4 spaces for indentation
- 88-100 character line length (Black-compatible)
- Single quotes for strings unless double quotes needed
- Trailing commas in multi-line collections
- Two blank lines between module-level functions/classes
- One blank line between methods

### Type Hints
- Required for function parameters and return types
- Use `from typing import Optional` for optional parameters
- Example: `def get_bytes(n: int, folds: int = 0) -> bytes:`

### Naming Conventions
- `snake_case` for functions, variables, modules
- `PascalCase` for classes
- `UPPER_CASE` for constants (module-level)
- Private functions/vars prefix with underscore: `_helper()`

### Docstrings
- Google-style docstrings with triple double-quotes
- Include Args, Returns, Raises sections
- Example:
  ```python
  def get_bytes(n: int) -> bytes:
      """Generate n random bytes from device.

      Args:
          n: Number of bytes to generate. Must be positive.

      Returns:
          Random bytes from hardware device.

      Raises:
          ValueError: If n <= 0
          RuntimeError: If device not found
      """
  ```

### Error Handling
- Use specific exceptions: `ValueError`, `RuntimeError`
- Include descriptive messages with f-strings
- Use bare `except Exception:` only for cleanup/fallbacks
- Always clean up resources in `finally` blocks
- Example:
  ```python
  try:
      ser.close()
  except Exception:
      pass
  ```

### API Design Patterns
- Each RNG module exposes consistent sync interface:
  - `is_device_available() -> bool`
  - `get_bytes(n: int) -> bytes`
  - `get_bits(n: int) -> bytes`
  - `get_exact_bits(n: int) -> bytes`
  - `random_int(min_val: int, max_val: int) -> int`
  - `close() -> None`
- Each function has an async version with `_async` suffix:
  - `get_bytes_async(n: int) -> bytes`
  - `get_bits_async(n: int) -> bytes`
  - `get_exact_bits_async(n: int) -> bytes`
  - `random_int_async(min_val: int, max_val: int) -> int`
  - `close_async() -> None`

### Hardware Device Handling
- Cache device handles (module-level `_cached_device`)
- Reset cache on errors
- Use try/finally for resource cleanup
- Add small delays after device operations (`time.sleep(0.1)`)

## Dependencies
- `pyserial>=3.5` - Serial port communication
- `pyusb>=1.3.1` - USB device access
- `secrets` (stdlib) - Software RNG

## Package Structure
```
rng_devices/
├── bitbabbler_rng/     # USB FTDI-based RNG
├── truerng/            # Serial port RNG
├── intel_seed/         # Intel/AMD CPU RDSEED instruction
└── pseudo_rng/         # Software fallback
```

Each package has `__init__.py` exposing public API via `__all__`.

## Environment
- Uses `uv` for package management (not pip)
- Virtual environment in `.venv/`
- Windows/Linux/macOS cross-platform support
