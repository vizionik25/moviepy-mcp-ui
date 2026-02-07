import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

try:
    from server import validate_math_expression
except ImportError as e:
    print(f"Could not import server.py directly: {e}")
    sys.exit(1)

def test_expr(expr, should_pass=True):
    print(f"Testing: {expr}")
    try:
        validate_math_expression(expr)
        if not should_pass:
            print(f"FAILED: Expected failure but passed for '{expr}'")
            return False
        print("PASSED (Allowed)")
        return True
    except ValueError as e:
        if should_pass:
            print(f"FAILED: Expected pass but failed for '{expr}': {e}")
            return False
        print(f"PASSED (Rejected): {e}")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception for '{expr}': {e}")
        return False

# Test cases
tests = [
    ("100 + 50*t", True),
    ("sin(t) * 100", True),
    ("t + pi", True),
    ("abs(t - 10)", True),
    ("where(t > 10, 1, 0)", True),
    ("100 ** 2", True),
    ("-t", True),
    # Malicious / Invalid
    ("__import__('os')", False),
    ("os.system('ls')", False),
    ("open('file')", False),
    ("[i for i in range(10)]", False),
    ("t.__class__", False),
    ("eval('1+1')", False),
    ("lambda x: x", False),
    ("1; print('hi')", False),
    ("exec('print(1)')", False),
    ("call_me(t)", False), # Unknown function
    ("x + 1", False), # Unknown variable (only t, pi, e allowed)
]

success = True
for expr, expected in tests:
    if not test_expr(expr, expected):
        success = False
    print("-" * 20)

if success:
    print("All security tests passed!")
    sys.exit(0)
else:
    print("Some tests failed.")
    sys.exit(1)
