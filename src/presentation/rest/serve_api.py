import uvicorn
import gradio as gr
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
from src.presentation.ui.app_ui import run_ui
from ...infra.postgres import database_async
from ...application import utils
from ...config import settings
from ..dependencies import *
from .routers import items


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
    utils.set_logger(level=settings.LOG_LEVEL)
    
    # # inject gradio
    # app_with_gradio = gr.mount_gradio_app(app, run_ui(launch_demo=False), path="/gradio")
    # uvicorn.run(app_with_gradio, host="0.0.0.0", port=8001)

    # without injecting gradio
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    run_api()
