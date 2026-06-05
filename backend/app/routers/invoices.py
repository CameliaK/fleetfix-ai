import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy import text
from app.db import engine
from app.services.pdf_extract import extract_supplier_invoice

router = APIRouter(prefix="/invoices", tags=["supplier-invoices"])

def get_or_create_supplier(conn, name: str) -> int:
    row = conn.execute(
        text("SELECT id FROM suppliers WHERE name = :n"), {"n": name}
    ).mappings().first()
    if row:
        return row["id"]
    return conn.execute(
        text("INSERT INTO suppliers (name) OUTPUT INSERTED.id VALUES (:n)"), {"n": name}
    ).scalar_one()

@router.post("/upload")
async def upload_supplier_invoice(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Save the upload to a temp file so pdfplumber can open it from disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        data = extract_supplier_invoice(tmp_path)
    except Exception as e:
        raise HTTPException(502, f"Extraction failed: {e}")
    finally:
        os.unlink(tmp_path)  # always clean up the temp file

    # Persist supplier + invoice + lines in one transaction
    with engine.begin() as conn:
        supplier_id = get_or_create_supplier(conn, data.supplier)
        invoice_id = conn.execute(
            text("""INSERT INTO supplier_invoices
                        (supplier_id, invoice_number, invoice_date, total, source_file)
                    OUTPUT INSERTED.id
                    VALUES (:s, :num, :date, :total, :file)"""),
            {"s": supplier_id, "num": data.invoice_number, "date": data.invoice_date,
             "total": data.total, "file": file.filename},
        ).scalar_one()
        for line in data.lines:
            conn.execute(
                text("""INSERT INTO supplier_invoice_lines
                            (supplier_invoice_id, description, quantity, unit_price)
                        VALUES (:i, :d, :q, :p)"""),
                {"i": invoice_id, "d": line.description, "q": line.quantity, "p": line.unit_price},
            )

    return {
        "supplier_invoice_id": invoice_id,
        "supplier": data.supplier,
        "invoice_number": data.invoice_number,
        "invoice_date": data.invoice_date,
        "total": data.total,
        "lines": [line.model_dump() for line in data.lines],
    }