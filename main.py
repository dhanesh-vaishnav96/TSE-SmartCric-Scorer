from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import history, match_routes
import uvicorn

app = FastAPI(title="🏏 TSE SmartCric Scorer")

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(history.router)
app.include_router(match_routes.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
