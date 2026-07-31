import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, PlainTextResponse
from contextlib import asynccontextmanager
from src.config import settings
from src.infra.logging import setup_logger
from src.presentation.dependencies import get_token, response_examples
from src.presentation.rest.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' The lifespan function to initialize the database before the app starts and close it after the app stops '''
    # await database.init_db()
    # await database.create_tables()
    yield    


app = FastAPI(
    lifespan=lifespan #, dependencies=[Depends(get_token)] # you can also add mandatory dependencies here [instead of only for items router],
)
app.include_router(items.router)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    ''' Redirect root page to /docs '''
    return RedirectResponse(url='/docs')


@app.get("/greet", response_class=PlainTextResponse)
async def greet_user():
    ''' Example endpoint to return a greeting message '''
    return PlainTextResponse(content="Hello to the API World", status_code=200)


def run_api():
    ''' Set the global logger level and run the API with specified host and port '''
    setup_logger(level=settings.LOG_LEVEL)

    # without injecting gradio
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    run_api()
