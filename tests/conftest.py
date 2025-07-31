import os
import pytest
import argparse
import asyncio
from src.infra.postgres.database_async import init_db, create_tables

@pytest.fixture(scope="session", autouse=True)
async def init_test_db_once(request):
    """
    Run once before db tests to initialize test DB schema/tables.
    """
    if not request.config.getoption("--with-db"):
        return
    await init_db()
    await create_tables(drop_first=True)

def pytest_addoption(parser):
    """Add custom CLI parameters to the pytest command"""

    # Add a command line option to control DB setup (to use only with test_db.py)
    parser.addoption("--with-db", action="store_true", default=None, help="Run tests with DB setup")

    # Create a parameter group for user defined custom options    
    p_group = parser.getgroup("custom", "Custom options")

    p_group.addoption("--access", action="store", default="local", choices=["local", "remote"],
                      help="Api access method.")
    p_group.addoption("--model", action="store", default="llama3.1",
                        choices=["llama3.1", "gpt4"],
                        help="Model mode to run.")
    p_group.addoption("--input_path", action="store", default="./data/example_inputs/", 
                      help="Input folder path with videos.")
    p_group.addoption("--output_file", action="store", default=None, 
                      help="Output file name with results.")
        
    parser.addoption("--get-help", action="store_true", help="Show custom options")


def pytest_configure(config: pytest.Config):
    if config.getoption("--get-help"):
        for group in config._parser._groups:
            if group.name == "custom":
                print("\nCustom Options:")
                for option in group.options:
                    # CLI flags: --model, --access, etc.
                    opts = ", ".join(option._long_opts + option._short_opts)

                    # Get help, default, and choices from internal _attrs dict
                    attrs = option._attrs
                    help_str = attrs.get("help", "")
                    default = attrs.get("default")
                    choices = attrs.get("choices")

                    # Format choices and default
                    details = []
                    if choices:
                        details.append(f"choices: {choices}")
                    if default is not None:
                        details.append(f"default: {default}")
                    if details:
                        help_str += f" ({'; '.join(details)})"

                    print(f"  {opts:<25} {help_str}")
                break
        else:
            print("No custom options group found.")

        pytest.exit("User-defined options are shown above.")


# Define a fixture for the arguments
@pytest.fixture
def args(pytestconfig):
    args = argparse.Namespace(
        access = pytestconfig.getoption("access"),
        model = pytestconfig.getoption("model"),
        input_path = pytestconfig.getoption("input_path"),
        output_file = pytestconfig.getoption("output_file"),
    )
    return args


def pytest_generate_tests(metafunc):
    if "question" in metafunc.fixturenames:
        # Get the path to examples.txt file
        examples_file_path = metafunc.config.getoption("--input_path") + '/example.txt'        
        # Ensure the file exists
        if os.path.exists(examples_file_path):
            with open(examples_file_path, 'r') as file:
                # Read the lines from the file
                lines = [line.strip() for line in file.readlines()]
            # Parametrize the test with the lines
            metafunc.parametrize("question", lines)
        else:
            raise FileNotFoundError(f"File not found at {examples_file_path}")
