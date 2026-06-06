from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.db import engine
from app.services.llm import clean_work_order

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

class WorkOrderIn(BaseModel):
    vehicle_id: int
    raw_text: str

class WorkOrderOut(BaseModel):
    id: int
    vehicle_id: int
    raw_text: str | None
    status: str

@router.post("", response_model=WorkOrderOut, status_code=201)
def create_work_order(order: WorkOrderIn):
    with engine.begin() as conn:  # begin() = transaction with auto-commit
        result = conn.execute(
            text("""
                INSERT INTO work_orders (vehicle_id, raw_text)
                OUTPUT INSERTED.id, INSERTED.vehicle_id, INSERTED.raw_text, INSERTED.status
                VALUES (:v, :t)
            """),
            {"v": order.vehicle_id, "t": order.raw_text},
        )
        return WorkOrderOut(**result.mappings().one())

@router.get("", response_model=list[WorkOrderOut])
def list_work_orders(status: str | None = None):
    sql = "SELECT id, vehicle_id, raw_text, status FROM work_orders"
    params = {}
    if status:
        sql += " WHERE status = :status"
        params["status"] = status
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        return [WorkOrderOut(**r) for r in rows]

@router.post("/{order_id}/invoice")
def generate_invoice(order_id: int):
    # 1. Fetch the raw text of the work order
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT raw_text FROM work_orders WHERE id = :id"),
            {"id": order_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(404, "Work order not found")

    # 2. Call the LLM (with error handling: the API can fail)
    try:
        invoice = clean_work_order(row["raw_text"])
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {e}")

    total = sum(line.quantity * line.unit_price for line in invoice.lines)

    # 3. Persist everything in a single transaction
    with engine.begin() as conn:
        conn.execute(
            text("""UPDATE work_orders
                    SET clean_text = :t, source_language = :lang, status = 'invoiced'
                    WHERE id = :id"""),
            {"t": invoice.work_summary, "lang": invoice.source_language, "id": order_id},
        )
        invoice_id = conn.execute(
            text("INSERT INTO invoices (work_order_id, total) OUTPUT INSERTED.id VALUES (:o, :total)"),
            {"o": order_id, "total": total},
        ).scalar_one()
        for line in invoice.lines:
            conn.execute(
                text("""INSERT INTO invoice_lines (invoice_id, description, quantity, unit_price)
                        VALUES (:i, :d, :q, :p)"""),
                {"i": invoice_id, "d": line.description, "q": line.quantity, "p": line.unit_price},
            )

    return {
        "invoice_id": invoice_id,
        "work_summary": invoice.work_summary,
        "source_language": invoice.source_language,
        "total": round(total, 2),
        "lines": [line.model_dump() for line in invoice.lines],
    }

@router.get("/{order_id}/invoice")
def get_invoice(order_id: int):
    with engine.connect() as conn:
        inv = conn.execute(
            text("""SELECT i.id AS invoice_id, i.total, i.currency,
                           w.clean_text, w.source_language, w.status
                    FROM invoices i
                    JOIN work_orders w ON w.id = i.work_order_id
                    WHERE i.work_order_id = :id"""),
            {"id": order_id},
        ).mappings().first()
        if inv is None:
            raise HTTPException(404, "No invoice for this work order")
        lines = conn.execute(
            text("""SELECT description, quantity, unit_price
                    FROM invoice_lines WHERE invoice_id = :iid"""),
            {"iid": inv["invoice_id"]},
        ).mappings().all()
    return {
        "invoice_id": inv["invoice_id"],
        "total": float(inv["total"]) if inv["total"] is not None else 0,
        "currency": inv["currency"],
        "clean_text": inv["clean_text"],
        "source_language": inv["source_language"],
        "status": inv["status"],
        "lines": [
            {"description": l["description"],
             "quantity": float(l["quantity"]),
             "unit_price": float(l["unit_price"])}
            for l in lines
        ],
    }

@router.post("/{order_id}/approve")
def approve_invoice(order_id: int):
    with engine.begin() as conn:
        result = conn.execute(
            text("UPDATE work_orders SET status = 'approved' WHERE id = :id"),
            {"id": order_id},
        )
        if result.rowcount == 0:
            raise HTTPException(404, "Work order not found")
    return {"order_id": order_id, "status": "approved"}