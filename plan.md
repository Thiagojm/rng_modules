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

### Design Decisions (Final)

1. **Executor Scope**: Module-level `ThreadPoolExecutor(max_workers=1)` per module
   - Prevents concurrent hardware access
   - One worker per RNG device
   - Isolated between modules

2. **Executor Shutdown**: In `close()` function
   - Shut down executor when `close()` is called
   - Releases resources properly

3. **is_device_available()**: No async version needed
   - Fast operation, synchronous is fine

4. **Cancellation Handling**: Option B - Add cleanup logic
   - Call `close()` on `CancelledError`
   - Ensures device state is reset

5. **Type Stubs**: Not needed now
   - Keep it simple

6. **Testing**: Test with actual hardware
   - All devices are connected
   - Test cancellation and edge cases

### 1. Add Async Variants to Each Module

**Pattern for each core.py:**

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

# Module-level executor (1 worker to prevent concurrent hardware access)
_executor = ThreadPoolExecutor(max_workers=1)

# Existing sync functions remain unchanged...

async def get_bytes_async(n: int) -> bytes:
    """Async version of get_bytes.
    
    Non-blocking for GUI applications. Uses thread pool executor
    to run sync operation in background thread.
    
    Args:
        n: Number of bytes to generate. Must be positive.
        
    Returns:
        Random bytes.
        
    Raises:
        ValueError: If n <= 0
        asyncio.CancelledError: If operation is cancelled
    """
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_bytes, n)
    except asyncio.CancelledError:
        # Cleanup on cancellation
        close()
        raise

async def get_bits_async(n: int) -> bytes:
    """Async version of get_bits."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_bits, n)
    except asyncio.CancelledError:
        close()
        raise

async def get_exact_bits_async(n: int) -> bytes:
    """Async version of get_exact_bits."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, get_exact_bits, n)
    except asyncio.CancelledError:
        close()
        raise

async def random_int_async(min_val: int = 0, max_val: Optional[int] = None) -> int:
    """Async version of random_int."""
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(_executor, random_int, min_val, max_val)
    except asyncio.CancelledError:
        close()
        raise

async def close_async() -> None:
    """Async version of close.
    
    Calls sync close() and shuts down the executor.
    """
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(_executor, close)
    finally:
        _executor.shutdown(wait=False)
```

### 2. Update Module Exports

Add async functions to `__all__` in each `__init__.py`:

```python
__all__ = [
    # Sync API
    "is_device_available",
    "get_bytes",
    "get_bits",
    "get_exact_bits",
    "random_int",
    "close",
    # Async API
    "get_bytes_async",
    "get_bits_async",
    "get_exact_bits_async",
    "random_int_async",
    "close_async",
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

**One comprehensive test file per module:** `test_[module]_async.py`

**Test structure:**

```python
import asyncio
import sys
from rng_devices import [module]

async def test_get_bytes_async():
    """Test basic async byte generation."""
    print("Testing get_bytes_async...")
    if not [module].is_device_available():
        print("  [SKIP] Device not available")
        return True
    
    try:
        data = await [module].get_bytes_async(32)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print("  [OK] get_bytes_async(32)")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_cancellation():
    """Test cancellation handling."""
    print("Testing cancellation...")
    if not [module].is_device_available():
        print("  [SKIP] Device not available")
        return True
    
    try:
        # Start a long operation and cancel it
        task = asyncio.create_task([module].get_bytes_async(1024))
        await asyncio.sleep(0.01)  # Let it start
        task.cancel()
        
        try:
            await task
        except asyncio.CancelledError:
            print("  [OK] Task cancelled properly")
            return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False

async def test_edge_cases():
    """Test edge cases and error handling."""
    print("Testing edge cases...")
    # Test invalid inputs, boundary conditions, etc.
    pass

async def main():
    """Run all async tests."""
    print(f"\nTesting [module] async methods...\n")
    
    results = []
    results.append(await test_get_bytes_async())
    results.append(await test_get_bits_async())
    results.append(await test_get_exact_bits_async())
    results.append(await test_random_int_async())
    results.append(await test_close_async())
    results.append(await test_cancellation())
    results.append(await test_edge_cases())
    
    print("\n" + "="*50)
    if all(results):
        print("SUCCESS: All async tests passed!")
        return 0
    else:
        print("FAILED: Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

**Test order:**
1. `test_pseudo_async.py` - Basic functionality (always available)
2. `test_intel_seed_async.py` - With RDSEED hardware
3. `test_truerng_async.py` - With TrueRNG device
4. `test_bitbabbler_async.py` - With BitBabbler device

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

## Implementation Phases

### Phase 1: pseudo_rng (Template Module)
- [ ] Add executor and async methods to `pseudo_rng/core.py`
- [ ] Update `pseudo_rng/__init__.py` exports
- [ ] Create `test_pseudo_async.py` with comprehensive tests
- [ ] Verify pattern works correctly

### Phase 2: Hardware RNG Modules
- [ ] Implement async for `intel_seed`
- [ ] Implement async for `truerng`
- [ ] Implement async for `bitbabbler_rng`
- [ ] Test each with actual hardware

### Phase 3: Documentation
- [ ] Update main README with async examples
- [ ] Add async usage section to each module's README
- [ ] Create PySide6 GUI integration example

## Timeline
1. ✅ IntelSeed compatibility fixes (completed)
2. ✅ Simplify rng_devices/__init__.py (completed)
3. ✅ Plan finalized (completed)
4. 🔄 Phase 1: pseudo_rng template (30 min)
5. 🔄 Phase 2: Hardware modules (1 hour)
6. 🔄 Phase 3: Documentation (30 min)

## Next Steps
**Starting Phase 1**: Implement async support for pseudo_rng module as the template.

**Implementation order:**
1. pseudo_rng/core.py - Add async methods
2. pseudo_rng/__init__.py - Update exports
3. test_pseudo_async.py - Create test file

Ready to start implementation now!
