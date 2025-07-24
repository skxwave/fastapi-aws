import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from src.api import api_router

app = FastAPI(title="FastAPI Backend + AWS Deploy")
app.include_router(api_router)


@app.route("/")
async def redirect_to_docs(request: Request):
    """
    Redirect to docs on the request to the root url of the app
    """
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        log_config=None,
        host="0.0.0.0",
        reload=True,
        port=8000,
    )
