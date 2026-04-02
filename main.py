import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import history, match_routes

app = FastAPI(title="🏏 TSE SmartCric Scorer")

# Mount Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Routers
app.include_router(history.router)
app.include_router(match_routes.router)

if __name__ == "__main__":
    # Get port from environment variable for deployment (Railway, Heroku, etc.)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
