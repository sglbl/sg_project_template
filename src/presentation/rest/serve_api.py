import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, PlainTextResponse, JSONResponse
from ..dependencies import *
from .routers import items


''' Run with:
python -m src.presentation.rest.serve_api
'''

app = FastAPI(
    # dependencies=[Depends(get_token)] # you can also add mandatory dependencies here [instead of only for items router]
)
app.include_router(items.router)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    ''' Redirect root page to /docs '''
    return RedirectResponse(url='/docs', status_code=308)


@app.get("/greet", response_class=PlainTextResponse)
async def greet_user():
    return PlainTextResponse(content="Hello to the API World", status_code=200)

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    run_api()