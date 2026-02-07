# RNG Library Async Support Implementation Plan

## Overview
Enhance the rng-modules library with optional async/await support using asyncio, making it suitable for GUI applications while remaining framework-agnostic. Maintain backward compatibility with existing synchronous methods.

**Status**: IntelSeed compatibility fixes completed, unified interface removed per user preference.

## Goals
- ✅ All RNG modules have compatible APIs (completed)
- ✅ Individual module imports supported (completed)
- 🔄 Add async variants of all RNG functions without breaking existing code
- 🔄 Support any asyncio-compatible GUI framework (PySide6, Tkinter+asyncio, etc.)
- 🔄 Enable non-blocking RNG operations in GUI applications
- ✅ Keep library dependencies minimal (asyncio is stdlib)

## Current State Assessment
- ✅ Library has four RNG modules: pseudo_rng, truerng, bitbabbler_rng, intel_seed
- ✅ Each module exposes consistent sync API: is_device_available, get_bytes, get_bits, get_exact_bits, random_int, close
- ✅ Individual module imports: `from rng_devices import intel_seed, truerng, ...`
- 🔄 Hardware RNGs may block during reads, unsuitable for GUI threads (needs async)

## Completed Work

### 1. IntelSeed API Compatibility
Fixed intel_seed module to match other modules:
- ✅ Renamed `is_rdseed_available()` → `is_device_available()` (with alias)
- ✅ Changed `random_int(low, high)` [inclusive] → `random_int(min_val, max_val)` [min_val, max_val) exclusive
- ✅ Added `close()` function
- ✅ Updated `__init__.py` exports

### 2. Simplified rng_devices/__init__.py
Removed unified auto-selection interface per user request. Now just exposes individual modules:

```python
from rng_devices import intel_seed, truerng, bitbabbler_rng, pseudo_rng

# GUI logic handles device selection and availability checking
if intel_seed.is_device_available():
    data = intel_seed.get_bytes(32)
```

## Implementation Plan

### 1. Add Async Variants to Each Module
For each core.py file, add async versions using thread pool executor:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Existing sync functions remain unchanged

async def get_bytes_async(n: int) -> bytes:
    """Async version of get_bytes. Non-blocking for GUI applications."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_bytes, n)

async def get_bits_async(n: int) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_bits, n)

async def get_exact_bits_async(n: int) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, get_exact_bits, n)

async def random_int_async(min_val: int = 0, max_val: Optional[int] = None) -> int:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, random_int, min_val, max_val)

async def close_async() -> None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, close)
```

**Note**: Using `_async` suffix instead of `a` prefix for clarity and Python convention.

### 2. Update Module Exports
Add async functions to `__all__` in each `__init__.py`:

```python
__all__ = [
    "is_device_available",
    "get_bytes", "get_bytes_async",
    "get_bits", "get_bits_async", 
    "get_exact_bits", "get_exact_bits_async",
    "random_int", "random_int_async",
    "close", "close_async",
]
```

### 3. Framework-Agnostic Design
- Use standard asyncio.run_in_executor() - works with any event loop
- No hard dependencies on GUI frameworks
- Optional PySide6 integration if available

### 4. Update Documentation
- Add async examples to each module's docstrings
- Create README section with GUI integration examples
- Document PySide6-specific usage with QtAsyncio

### 5. Testing
- Add async test cases for each module
- Test with multiple event loops (asyncio.run, QtAsyncio.run)
- Verify cancellation works properly

### 6. Dependencies
- Keep asyncio as stdlib (no new required deps)
- Add PySide6 as optional dependency for Qt integration examples

## Usage Examples

### PySide6 GUI with Individual Modules
```python
import PySide6.QtAsyncio as QtAsyncio
from rng_devices import intel_seed, pseudo_rng
import asyncio

class RNGWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_rng = intel_seed  # User selects this in GUI
        
    async def generate_data(self):
        if self.selected_rng.is_device_available():
            data = await self.selected_rng.get_bytes_async(32)
            # Update UI
        else:
            # Show error: device not connected
            pass

async def main():
    app = QApplication(sys.argv)
    window = RNGWindow()
    window.show()
    await asyncio.Event().wait()

QtAsyncio.run(main())
```

### Generic Asyncio
```python
import asyncio
from rng_devices import pseudo_rng

async def main():
    data = await pseudo_rng.get_bytes_async(32)
    print(data)

asyncio.run(main())
```

## Benefits
- **Framework Agnostic**: Works with any asyncio-compatible GUI
- **Backward Compatible**: Existing sync code continues to work
- **Non-blocking**: GUI remains responsive during RNG operations
- **Concurrent**: Multiple RNG requests can run simultaneously
- **Cancellation**: Async operations can be cancelled gracefully
- **GUI Flexibility**: User can select any device, GUI handles availability

## Risks & Mitigations
- **Threading Overhead**: run_in_executor adds minimal overhead - acceptable for GUI use
- **Hardware RNG Blocking**: Serial operations still block thread, but isolated from GUI thread
- **Complexity**: Async code is more complex - provide clear sync/async examples

## Timeline
1. ✅ IntelSeed compatibility fixes (completed)
2. ✅ Simplify rng_devices/__init__.py (completed)
3. 🔄 Implement async variants in all modules (1-2 hours)
4. 🔄 Update documentation and examples (1 hour)
5. 🔄 Add tests (1 hour)
6. 🔄 Integration testing with PySide6 (30 min)

## Next Steps
Ready to implement async variants in all four modules. Should I proceed?
