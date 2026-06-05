import pdfplumber
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class SupplierLine(BaseModel):
    description: str
    quantity: float
    unit_price: float

class SupplierInvoiceData(BaseModel):
    supplier: str
    invoice_number: str
    invoice_date: str          # ISO format YYYY-MM-DD
    total: float
    lines: list[SupplierLine]

def pdf_to_text(path: str) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)

def extract_supplier_invoice(path: str) -> SupplierInvoiceData:
    raw = pdf_to_text(path)
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": (
                "Extract this supplier invoice into structured JSON. "
                "Return invoice_date in ISO format YYYY-MM-DD. "
                "Use the grand total (after taxes) for 'total'. "
                "Do not invent values that are not present in the document."
            )},
            {"role": "user", "content": raw},
        ],
        response_format=SupplierInvoiceData,
    )
    return completion.choices[0].message.parsed