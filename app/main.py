from api.v1.routers import file, forgot, health, login, project, register, user
from core.config import settings
from fastapi import FastAPI, responses
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

app = FastAPI(
    title="Mannequins API",
    version=settings.releaseId,
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_pagination(app)


app.include_router(health.router, tags=["health"], prefix=settings.API_V1_STR)


app.include_router(login.router, tags=["user"], prefix=settings.API_V1_STR)
app.include_router(register.router, tags=["user"], prefix=settings.API_V1_STR)
app.include_router(user.router, tags=["user"], prefix=settings.API_V1_STR)
app.include_router(forgot.router, tags=["user"], prefix=settings.API_V1_STR)


app.include_router(
    project.router, tags=["project"], prefix=settings.API_V1_STR
)

app.include_router(file.router, tags=["file"], prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def index() -> responses.RedirectResponse:
    return responses.RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, port=8000, host="0.0.0.0")
