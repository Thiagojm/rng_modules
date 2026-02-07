# RNG Modules

Hardware and software random number generator modules for Python. Supports multiple RNG sources with a consistent API.

## Supported RNG Sources

- **Intel RDSEED** (`intel_seed`): Intel/AMD CPU hardware RNG (Intel Broadwell 2014+ or AMD Zen 2017+)
- **TrueRNG** (`truerng`): USB hardware RNG devices from ubld.it
- **BitBabbler** (`bitbabbler_rng`): USB hardware RNG devices from bitbabbler.org
- **Software RNG** (`pseudo_rng`): Python's `secrets` module fallback (always available)

## Requirements

- Python 3.13+
- Intel RDSEED: Compatible CPU with librdseed library
- TrueRNG: USB device with pyserial
- BitBabbler: USB device with pyusb

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| **Windows** | ✅ Supported | Tested and working |
| **Linux** | ✅ Supported | Should work (uses platform-agnostic code) |
| **macOS** | ❌ Not supported | No `.dylib` library available |

The library is designed to be cross-platform for Windows and Linux:
- Intel RDSEED includes both `librdseed.dll` (Windows) and `librdseed.so` (Linux)
- TrueRNG uses pyserial which works on both platforms
- BitBabbler uses pyusb with platform detection for libusb
- Pseudo RNG is pure Python and works everywhere

## Installation

```bash
uv sync
```

## Usage

### Basic Usage

```python
from rng_devices import intel_seed, pseudo_rng

# Check if Intel RDSEED is available
if intel_seed.is_device_available():
    data = intel_seed.get_bytes(32)
    print(f"Hardware RNG: {data.hex()}")
else:
    # Fallback to software RNG
    data = pseudo_rng.get_bytes(32)
    print(f"Software RNG: {data.hex()}")
```

### All Modules Expose Consistent API

```python
from rng_devices import intel_seed, truerng, bitbabbler_rng, pseudo_rng

for module in [intel_seed, truerng, bitbabbler_rng, pseudo_rng]:
    if module.is_device_available():
        # All modules have the same interface:
        data = module.get_bytes(32)                    # Generate 32 bytes
        bits = module.get_bits(256)                    # Generate 256 bits
        exact_bits = module.get_exact_bits(128)        # Generate exactly 128 bits
        num = module.random_int(1, 100)                # Random int [1, 100)
        module.close()                                 # Cleanup resources
```

### Available Functions

All modules expose:

- `is_device_available() -> bool`: Check if device is accessible
- `get_bytes(n: int) -> bytes`: Generate n random bytes
- `get_bits(n: int) -> bytes`: Generate at least n bits (rounds up to bytes)
- `get_exact_bits(n: int) -> bytes`: Generate exactly n bits (must be divisible by 8)
- `random_int(min_val: int = 0, max_val: Optional[int] = None) -> int`: Random integer [min_val, max_val)
- `close() -> None`: Cleanup resources

### Testing Individual Modules

```bash
# Test each RNG module
uv run python rng_devices/test_pseudo.py
uv run python rng_devices/test_true.py
uv run python rng_devices/test_bit.py
uv run python rng_devices/test_intel_seed.py
```

### API Compatibility Test

```bash
uv run python test_api_compatibility.py
```

## Module Details

### Intel RDSEED
Fastest RNG using CPU hardware instructions. See `rng_devices/intel_seed/README.md` for build instructions.

### TrueRNG
USB serial RNG devices. Requires `pyserial`.

### BitBabbler
USB FTDI-based RNG devices. Requires `pyusb`.

### Pseudo RNG
Software fallback using Python's `secrets` module. Always available, no dependencies.

## Project Structure

```
rng_devices/
├── intel_seed/          # Intel RDSEED CPU instruction
├── truerng/            # TrueRNG USB devices
├── bitbabbler_rng/     # BitBabbler USB devices
└── pseudo_rng/         # Software fallback
```

## License

MIT License
