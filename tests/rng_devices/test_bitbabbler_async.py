"""
Async test script for bitbabbler_rng module.

Tests all async methods with actual hardware operations and cancellation.
"""

import asyncio
import sys


def test_sync_api_still_works():
    """Verify sync API wasn't broken."""
    print("Testing sync API compatibility...")
    from bitbabbler_rng import is_device_available, get_bytes, random_int, close

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        # Test sync functions still work
        data = get_bytes(16)
        assert len(data) == 16, f"Expected 16 bytes, got {len(data)}"

        num = random_int(1, 100)
        assert 1 <= num < 100, f"Random int out of range: {num}"

        close()  # Should not raise

        print("  [OK] Sync API works correctly")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_get_bytes_async():
    """Test basic async byte generation."""
    print("Testing get_bytes_async...")
    from bitbabbler_rng import is_device_available, get_bytes_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        # Test without folding
        data = await get_bytes_async(32)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_bytes_async(32) returned {len(data)} bytes")

        # Test with folding
        data = await get_bytes_async(32, folds=2)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_bytes_async(32, folds=2) returned {len(data)} bytes")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_get_bits_async():
    """Test async bit generation."""
    print("Testing get_bits_async...")
    from bitbabbler_rng import is_device_available, get_bits_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        data = await get_bits_async(100)
        expected_bytes = (100 + 7) // 8  # 13 bytes
        assert len(data) == expected_bytes, (
            f"Expected {expected_bytes} bytes, got {len(data)}"
        )
        print(
            f"  [OK] get_bits_async(100) returned {len(data)} bytes ({len(data) * 8} bits)"
        )
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_get_exact_bits_async():
    """Test async exact bit generation."""
    print("Testing get_exact_bits_async...")
    from bitbabbler_rng import is_device_available, get_exact_bits_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        data = await get_exact_bits_async(256)
        assert len(data) == 32, f"Expected 32 bytes, got {len(data)}"
        print(f"  [OK] get_exact_bits_async(256) returned {len(data)} bytes")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_random_int_async():
    """Test async random integer generation."""
    print("Testing random_int_async...")
    from bitbabbler_rng import is_device_available, random_int_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        # Test with range
        results = set()
        for _ in range(50):
            val = await random_int_async(0, 10)
            results.add(val)
            assert 0 <= val < 10, f"Value {val} out of range [0, 10)"

        print(f"  [OK] random_int_async(0, 10) returned values: {sorted(results)}")

        # Test without range (32-bit)
        val = await random_int_async()
        assert isinstance(val, int), "Should return int"
        print(f"  [OK] random_int_async() returned 32-bit int")

        # Test with folding
        val = await random_int_async(0, 100, folds=1)
        assert 0 <= val < 100, f"Value {val} out of range [0, 100)"
        print(f"  [OK] random_int_async(0, 100, folds=1) returned {val}")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_close_async():
    """Test async close."""
    print("Testing close_async...")
    print("  [NOTE] This test should be run last as it shuts down the executor")
    from bitbabbler_rng import close_async

    try:
        await close_async()
        print("  [OK] close_async executed successfully")
        print("  [NOTE] Executor shut down - async operations will fail after this")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_cancellation():
    """Test cancellation handling."""
    print("Testing cancellation handling...")
    from bitbabbler_rng import is_device_available, get_bytes_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        # Start operation and cancel immediately
        task = asyncio.create_task(get_bytes_async(1024))  # Large request
        await asyncio.sleep(0.001)  # Let it start
        task.cancel()

        try:
            await task
            print("  [WARN] Task completed without cancellation")
        except asyncio.CancelledError:
            print("  [OK] Task cancelled properly")

        # Verify module still works after cancellation
        data = await get_bytes_async(32)
        assert len(data) == 32
        print("  [OK] Module still works after cancellation")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_error_handling():
    """Test error handling in async operations."""
    print("Testing error handling...")
    from bitbabbler_rng import (
        is_device_available,
        get_bytes_async,
        get_exact_bits_async,
        random_int_async,
    )

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    errors_caught = 0

    try:
        # Test negative bytes
        try:
            await get_bytes_async(-1)
            print("  [FAIL] Should have raised ValueError for negative bytes")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for negative bytes")

        # Test non-divisible bits
        try:
            await get_exact_bits_async(100)  # Not divisible by 8
            print("  [FAIL] Should have raised ValueError for non-divisible bits")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for non-divisible bits")

        # Test invalid random range
        try:
            await random_int_async(10, 5)  # min > max
            print("  [FAIL] Should have raised ValueError for invalid range")
        except ValueError:
            errors_caught += 1
            print("  [OK] ValueError raised for invalid range")

        return errors_caught == 3
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def test_multiple_concurrent():
    """Test multiple concurrent async operations."""
    print("Testing concurrent operations...")
    from bitbabbler_rng import is_device_available, get_bytes_async

    if not is_device_available():
        print("  [SKIP] BitBabbler device not connected")
        return True

    try:
        # Start multiple operations concurrently
        tasks = [
            get_bytes_async(32),
            get_bytes_async(64),
            get_bytes_async(128),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results[0]) == 32, "First result wrong size"
        assert len(results[1]) == 64, "Second result wrong size"
        assert len(results[2]) == 128, "Third result wrong size"

        print(f"  [OK] Completed {len(tasks)} concurrent operations")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


async def main():
    """Run all async tests."""
    print("\n" + "=" * 60)
    print("Testing BitBabbler Async Methods")
    print("=" * 60 + "\n")

    results = []

    # Test sync API wasn't broken
    results.append(test_sync_api_still_works())
    print()

    # Test async methods (close_async should be last as it shuts down executor)
    results.append(await test_get_bytes_async())
    results.append(await test_get_bits_async())
    results.append(await test_get_exact_bits_async())
    results.append(await test_random_int_async())
    results.append(await test_cancellation())
    results.append(await test_error_handling())
    results.append(await test_multiple_concurrent())
    results.append(await test_close_async())  # Must be last

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
    sys.exit(asyncio.run(main()))
