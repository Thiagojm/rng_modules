"""
Test script for bitbabbler_rng module.

Tests all sync methods.
"""

import sys


def test_is_device_available():
    """Test device availability check."""
    print("Testing is_device_available...")
    from rng_devices.bitbabbler_rng import is_device_available

    try:
        result = is_device_available()
        print(f"  [OK] is_device_available() returned: {result}")
    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_get_bytes():
    """Test basic byte generation."""
    print("Testing get_bytes...")
    from rng_devices.bitbabbler_rng import is_device_available, get_bytes

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return

    try:
        # Test without folding
        data = get_bytes(32)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_bytes(32) returned {len(data)} bytes")

        # Test with folding
        data = get_bytes(32, folds=2)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_bytes(32, folds=2) returned {len(data)} bytes")

    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_get_bits():
    """Test bit generation."""
    print("Testing get_bits...")
    from rng_devices.bitbabbler_rng import is_device_available, get_bits

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return

    try:
        data = get_bits(100)
        expected_bytes = (100 + 7) // 8  # 13 bytes
        assert len(data) == expected_bytes, (
            f"Expected {expected_bytes} bytes, got {len(data)}"
        )
        print(f"  [OK] get_bits(100) returned {len(data)} bytes ({len(data) * 8} bits)")
    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_get_exact_bits():
    """Test exact bit generation."""
    print("Testing get_exact_bits...")
    from rng_devices.bitbabbler_rng import is_device_available, get_exact_bits

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return

    try:
        data = get_exact_bits(256)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_exact_bits(256) returned {len(data)} bytes")
    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_random_int():
    """Test random integer generation."""
    print("Testing random_int...")
    from rng_devices.bitbabbler_rng import is_device_available, random_int

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return

    try:
        # Test with range
        results = set()
        for _ in range(50):
            val = random_int(0, 10)
            results.add(val)
            assert 0 <= val < 10, f"Value {val} out of range [0, 10)"

        print(f"  [OK] random_int(0, 10) returned values: {sorted(results)}")

        # Test without range (32-bit)
        val = random_int()
        assert isinstance(val, int), "Should return int"
        print("  [OK] random_int() returned 32-bit int")

        # Test with folding
        val = random_int(0, 100, folds=1)
        assert 0 <= val < 100, f"Value {val} out of range [0, 100)"
        print(f"  [OK] random_int(0, 100, folds=1) returned {val}")

    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_close():
    """Test close."""
    print("Testing close...")
    from rng_devices.bitbabbler_rng import close

    try:
        close()  # Should not raise
        print("  [OK] close executed successfully")
    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    from rng_devices.bitbabbler_rng import (
        is_device_available,
        get_bytes,
        get_exact_bits,
        random_int,
    )

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    errors_caught = 0

    try:
        # Test negative bytes
        try:
            get_bytes(-1)
            print("  [FAIL] Should have raised ValueError for negative bytes")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for negative bytes")

        # Test non-divisible bits
        try:
            get_exact_bits(100)  # Not divisible by 8
            print("  [FAIL] Should have raised ValueError for non-divisible bits")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for non-divisible bits")

        # Test invalid random range
        try:
            random_int(10, 5)  # min > max
            print("  [FAIL] Should have raised ValueError for invalid range")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for invalid range")

        assert errors_caught == 3, f"Expected 3 errors, got {errors_caught}"
    except Exception as e:
        print(f"  [FAIL] {e}")
        raise


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Testing BitBabbler Sync Methods")
    print("=" * 60 + "\n")

    results = []

    results.append(test_is_device_available())
    results.append(test_get_bytes())
    results.append(test_get_bits())
    results.append(test_get_exact_bits())
    results.append(test_random_int())
    results.append(test_error_handling())
    results.append(test_close())

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)

    if all(results):
        print(f"SUCCESS: All {total} tests passed!")
        return 0
    else:
        print(f"FAILED: {passed}/{total} tests passed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
