"""
pytest -s --tb=no tests/test_static.py
"""
import pyright


def test_with_pyright():
    """ Run pyright to check for static type errors in the codebase. """
    response = pyright.cli.run()
    assert response.returncode == 0, f"Pyright return code was {response.returncode}, expected 0. Please check the output for static errors."
