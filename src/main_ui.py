""" Main application logic (e.g., initializing models, handling input/output) """
if __name__ == "__main__":
    try: 
        from src.presentation.ui.app_ui import run_ui
        from src.presentation.bootstrap import create_services

        # Initialize services once, outside UI
        services = create_services(model="postgres")
        run_ui(services=services)
    except ModuleNotFoundError as e:
        import os
        if e.name == "src":
            print(f"{e}, running the app with '\033[92mpython -m src.main_ui'\033[0m instead!")
            os.system("python -m src.main")
        else:
            print(f'Error: {e}. Please check the modules!\n')
            raise e
