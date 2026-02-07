"""
Test the simplified RNG interface - individual module access.
"""

import sys


def test_individual_modules():
    """Test that individual modules can be imported and used."""
    print("Testing Individual Module Access...\n")

    errors = []

    try:
        # Import all modules
        from rng_devices import intel_seed, truerng, bitbabbler_rng, pseudo_rng

        print("[OK] Successfully imported all modules")

        modules = [
            ("intel_seed", intel_seed),
            ("truerng", truerng),
            ("bitbabbler_rng", bitbabbler_rng),
            ("pseudo_rng", pseudo_rng),
        ]

        for name, module in modules:
            print(f"\nTesting {name}...")

            # Check all expected functions exist
            expected_functions = [
                "is_device_available",
                "get_bytes",
                "get_bits",
                "get_exact_bits",
                "random_int",
                "close",
            ]

            for func_name in expected_functions:
                if hasattr(module, func_name):
                    print(f"  [OK] {func_name}")
                else:
                    errors.append(f"{name}: Missing function '{func_name}'")
                    print(f"  [FAIL] {func_name} missing")

            # Test is_device_available
            try:
                available = module.is_device_available()
                print(f"  [OK] is_device_available() = {available}")
            except Exception as e:
                errors.append(f"{name}: is_device_available() failed: {e}")
                print(f"  [FAIL] is_device_available() failed: {e}")

            # If available, test basic operations
            if hasattr(module, "is_device_available") and module.is_device_available():
                try:
                    # Test get_bytes
                    data = module.get_bytes(32)
                    if len(data) == 32:
                        print(f"  [OK] get_bytes(32) works")
                    else:
                        errors.append(f"{name}: get_bytes returned {len(data)} bytes")
                        print(f"  [FAIL] get_bytes returned wrong size")

                    # Test random_int
                    val = module.random_int(0, 10)
                    if 0 <= val < 10:
                        print(f"  [OK] random_int(0, 10) = {val}")
                    else:
                        errors.append(f"{name}: random_int returned {val}")
                        print(f"  [FAIL] random_int out of range")

                except Exception as e:
                    errors.append(f"{name}: Basic operations failed: {e}")
                    print(f"  [FAIL] Basic operations failed: {e}")

    except ImportError as e:
        errors.append(f"Failed to import modules: {e}")
        print(f"[FAIL] Failed to import modules: {e}")

    # Summary
    print("\n" + "=" * 50)
    if errors:
        print(f"FAILED: {len(errors)} error(s) found")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("SUCCESS: All modules work correctly!")
        return True


if __name__ == "__main__":
    success = test_individual_modules()
    sys.exit(0 if success else 1)
