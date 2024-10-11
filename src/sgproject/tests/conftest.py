import os
import pytest
import argparse

def pytest_addoption(parser):
    """Add custom CLI parameters to the pytest command"""

    # Create a parameter group for user defined custom options    
    p_group = parser.getgroup("custom", "Custom options")

    p_group.addoption("--access", action="store", default="local")
    p_group.addoption("--model", action="store", default="llama3.1")
    p_group.addoption("--input_path", action="store", default="./data/example_inputs/")
    p_group.addoption("--output_file", action="store", default=None)
        
    parser.addoption("--test-help", action="store_true", help="Show custom options")


def pytest_configure(config: pytest.Config):
    # Additional help message for the user with "--test-help" option
    if config.getoption("--test-help"):
        print("""\nCustom Options:
            --access=ACCESS       Api access method [local, cloud]
            --model=MODEL         Model mode to run [llama3.1, gpt4]
            --input_path=INPUT_PATH   Input folder path with videos
            --output_file=OUTPUT_FILE   Output file name with results
        """)

        pytest.exit("User defined options are shown.")


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
        examples_file_path = metafunc.config.getoption("--input_path") + '/questionsmini.txt'        
        # Ensure the file exists
        if os.path.exists(examples_file_path):
            with open(examples_file_path, 'r') as file:
                # Read the lines from the file
                lines = [line.strip() for line in file.readlines()]
            # Parametrize the test with the lines
            metafunc.parametrize("question", lines)
        else:
            raise FileNotFoundError(f"File not found at {examples_file_path}")
