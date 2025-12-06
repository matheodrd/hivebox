from fastapi import FastAPI

from hivebox.version import version

app = FastAPI(title="Hivebox")


@app.get("/version")
async def get_version() -> str:
    return version()
