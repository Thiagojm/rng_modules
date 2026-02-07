from rng_devices.intel_seed import (
    is_device_available,
    get_bytes,
    get_bits,
    get_exact_bits,
    random_int,
)
import time

t0 = time.time()
# Check if device is connected
if is_device_available():
    # Generate 32 bytes of raw entropy
    raw = get_bytes(32)
    print(raw)

    # Generate 100 random bits (returns 13 bytes, 104 bits total)
    data1 = get_bits(100)
    print(data1)

    # Generate exactly 128 random bits (16 bytes)
    data2 = get_exact_bits(128)
    print(data2)

    # Count ones for statistical analysis
    ones = sum(bin(b).count("1") for b in data2)
    zeros = len(data2) * 8 - ones
    print(ones)
    print(zeros)

    # Test random_int
    num1 = random_int(0, 100)
    print(f"Random int 0-99: {num1}")

    num2 = random_int(1, 6)  # Like a die roll
    print(f"Random int 1-5: {num2}")

else:
    print("Intel RDSEED not available")

t1 = time.time() - t0
print(f"Time: {t1:.4f} seconds")
