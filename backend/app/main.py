from fastapi import FastAPI
from app.routers import work_orders, invoices, predictions

app = FastAPI(title="FleetFix AI")
app.include_router(work_orders.router)
app.include_router(invoices.router)
app.include_router(predictions.router)


@app.get("/health")
def health():
    return {"status": "ok"}