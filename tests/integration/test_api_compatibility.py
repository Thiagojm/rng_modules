"""
Test script to verify all RNG modules have compatible APIs.
"""

import sys


def test_api_compatibility():
    """Test that all RNG modules expose compatible APIs."""
    errors = []

    # Expected functions and their signatures
    expected_functions = [
        "is_device_available",
        "get_bytes",
        "get_bits",
        "get_exact_bits",
        "random_int",
        "close",
    ]

    modules_to_test = [
        ("pseudo_rng", "rng_devices.pseudo_rng"),
        ("truerng", "rng_devices.truerng"),
        ("bitbabbler_rng", "rng_devices.bitbabbler_rng"),
        ("intel_seed", "rng_devices.intel_seed"),
    ]

    print("Testing RNG module API compatibility...\n")

    for module_name, module_path in modules_to_test:
        print(f"Testing {module_name}...")
        try:
            # Import the module
            module = __import__(module_path, fromlist=[module_name])

            # Check all expected functions exist
            for func_name in expected_functions:
                if not hasattr(module, func_name):
                    error_msg = (
                        f"  [FAIL] {module_name}: Missing function '{func_name}'"
                    )
                    errors.append(error_msg)
                    print(error_msg)
                else:
                    print(f"  [OK] {func_name}")

            # Check is_device_available() is callable
            if hasattr(module, "is_device_available"):
                try:
                    result = module.is_device_available()
                    print(f"  [OK] is_device_available() returned: {result}")
                except Exception as e:
                    error_msg = f"  [WARN] {module_name}: is_device_available() raised {type(e).__name__}: {e}"
                    errors.append(error_msg)
                    print(error_msg)

            print()

        except ImportError as e:
            error_msg = f"  [FAIL] {module_name}: Failed to import - {e}"
            errors.append(error_msg)
            print(error_msg)
            print()

    # Summary
    print("=" * 50)
    if errors:
        print(f"FAILED: {len(errors)} error(s) found")
        for error in errors:
            print(f"  - {error}")
        assert False, f"{len(errors)} API compatibility error(s) found"
    else:
        print("SUCCESS: All modules have compatible APIs!")


def test_random_int_semantics():
    """Test that random_int works consistently across modules."""
    print("\nTesting random_int semantics...\n")

    errors = []

    modules_to_test = [
        ("pseudo_rng", "rng_devices.pseudo_rng"),
    ]

    # Only test pseudo_rng since hardware may not be available
    for module_name, module_path in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[module_name])

            # Test range [0, 10) - should return 0-9
            results = set()
            for _ in range(100):
                val = module.random_int(0, 10)
                results.add(val)
                if val < 0 or val >= 10:
                    errors.append(
                        f"{module_name}: random_int(0, 10) returned {val}, expected [0, 10)"
                    )

            print(
                f"  [OK] {module_name}: random_int(0, 10) returned values in range [0, 10)"
            )
            print(f"    Sample values: {sorted(list(results))[:10]}")

        except Exception as e:
            errors.append(f"{module_name}: Error testing random_int - {e}")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        assert False, f"{len(errors)} random_int semantic error(s)"
    else:
        print("\n[OK] random_int semantics are correct!")


if __name__ == "__main__":
    success = test_api_compatibility()
    success = test_random_int_semantics() and success

    sys.exit(0 if success else 1)
