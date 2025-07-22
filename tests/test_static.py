import pyright

"""
pytest -s --tb=no tests/test_static.py
"""

def test_with_pyright():
    # Run pyright
    response = pyright.cli.run()
    assert response.returncode == 0, f"Pyright return code was {response.returncode}, expected 0. Please check the output for static errors."
    