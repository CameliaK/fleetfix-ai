from fastapi import FastAPI
from app.routers import work_orders

app = FastAPI(title="FleetFix AI")
app.include_router(work_orders.router)

@app.get("/health")
def health():
    return {"status": "ok"}