""" Main api application """
if __name__ == "__main__":
    try: 
        from src.presentation.rest import serve_api
        serve_api.run_api()
    except ModuleNotFoundError as e:
        START_COLORED_LOG = "\033[92m"
        END_COLORED_LOG = "\033[0m"
        print(f'{e}, please run:{START_COLORED_LOG} python -m src.main_api {END_COLORED_LOG}')
