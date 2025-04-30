if __name__ == "__main__":
    try: 
        from src.presentation.rest import serve_api
        serve_api.run_api()
    except ModuleNotFoundError as e:
        import os
        module_to_run = "main_api"
        if e.name == "src":
            print(f"{e}, running the app with '\033[92mpython -m src.{module_to_run}'\033[0m instead!")
            os.system(f"python -m src.{module_to_run}")
        else:
            print(f'Error: {e}. Please check the modules!\n')
            raise e
