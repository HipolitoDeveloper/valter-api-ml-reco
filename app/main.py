from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="Valter Reco API")

app.include_router(routes.router)