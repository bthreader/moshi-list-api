"""Runs the API server"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Fast
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Other
from pymongo import MongoClient

# Module
from main.config import config
from main.routers import tasks, lists

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

app = FastAPI()

# Allow the front-end dev server and the production server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://bthreader.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_client():
    """Creates a database connection"""
    app.mongodb_client = MongoClient(host=config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]


@app.on_event("shutdown")
def shutdown_db_client():
    """Closes the database connection"""
    app.mongodb_client.close()


app.include_router(tasks.router)
app.include_router(lists.router)
