import argparse
from src.presentation.ui import gradio_ui

def argument_parser():
    # Argument parsing logic
    llm_models = ['gemma', 'mistral', 'gemma:2b', 'gemma:7b', "none"]
    embedding_models = ["bge-m3", "bge-m3-unsupervised", "nomic-embed-text-v1", "multilingual-e5-large-instruct"] # even worse: #"bge-large-en-v1.5" #"all-MiniLM-L6-v2" # or "all-mpnet-base-v2"
    # Define the parser
    des = """This is an application for Deduce GPT. You can define the model using --llm or/and --embedding"""
    epi = """Example: python app.py [--embedding bge-m3]"""
    parser = argparse.ArgumentParser(description=des, epilog=epi)
    
    o_group = parser.add_argument_group('Optional Arguments')
    o_group.add_argument('--llm', required=False, type=str, choices=llm_models, default="gemma", help="Model to run (default: none)")
    o_group.add_argument('--embedding', required=False, type=str, choices=embedding_models, default="bge-m3", help="Embedding model to run (default: bge-m3)")
    return parser.parse_known_args()[0]


def main():
    # Main application logic (e.g., initializing models, handling input/output)
    # Parse the arguments to get the model name
    args = argument_parser()
    print(f'LLM: {args.llm}')
    # Create the model
    gradio_ui.run_ui()
    

if __name__ == "__main__":
    main()