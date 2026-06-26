from fastapi import FastAPI
from dashboard.routes import router
from database.db import init_db
from scheduler.tasks import start_scheduler
import uvicorn

app = FastAPI(title="College Mail Guardian API")

@app.on_event("startup")
def startup_event():
    init_db()
    start_scheduler()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)