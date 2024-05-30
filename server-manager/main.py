import os
import subprocess
from typing import Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse

app = FastAPI()


AUTH_ERROR = "AUTH_ERROR", "authentication failed"
DB_INVALID_PATH = "DB_INVALID_PATH", "database path does not exist"


with open("token", "r") as token_file:
    token = token_file.read().strip()


def error(error_: Tuple[str, str]):
    return JSONResponse(
        status_code=200,
        content={"code": error_[0], "message": error_[1]},
    )


@app.middleware("http")
async def authenticate(request: Request, call_next):
    request_token = request.headers.get("Authorization", None)

    if request_token is None:
        return error(AUTH_ERROR)

    if not request_token.startswith("Bearer "):
        return error(AUTH_ERROR)

    request_token = request_token.replace("Bearer ", "")
    if request_token != token:
        return error(AUTH_ERROR)

    response = await call_next(request)
    return response


@app.get("/get-db/")
async def download_database():
    path = "/etc/x-ui/x-ui.db"

    if not os.path.exists(path):
        return error(DB_INVALID_PATH)
    return FileResponse(path, filename="x-ui.db")


@app.get("/restart-panel/")
async def restart_panel():
    return_code = subprocess.run(["systemctl", "restart", "x-ui"], shell=True)
    return {"success": return_code.returncode == 0}


@app.get("/restart-nginx/")
async def restart_nginx():
    return_code = subprocess.run(["systemctl", "restart", "nginx"], shell=True)
    return {"success": return_code.returncode == 0}
