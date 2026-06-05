from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text
from app.db import engine

router = APIRouter(prefix="/work-orders", tags=["work-orders"])

class OrdenIn(BaseModel):
    vehiculo_id: int
    texto_crudo: str

class OrdenOut(BaseModel):
    id: int
    vehiculo_id: int
    texto_crudo: str | None
    estado: str

@router.post("", response_model=OrdenOut, status_code=201)
def crear_orden(orden: OrdenIn):
    with engine.begin() as conn:          # begin() = transacción con commit automático
        result = conn.execute(
            text("""
                INSERT INTO ordenes_trabajo (vehiculo_id, texto_crudo)
                OUTPUT INSERTED.id, INSERTED.vehiculo_id, INSERTED.texto_crudo, INSERTED.estado
                VALUES (:v, :t)
            """),
            {"v": orden.vehiculo_id, "t": orden.texto_crudo},
        )
        return OrdenOut(**result.mappings().one())

@router.get("", response_model=list[OrdenOut])
def listar_ordenes(estado: str | None = None):
    sql = "SELECT id, vehiculo_id, texto_crudo, estado FROM ordenes_trabajo"
    params = {}
    if estado:
        sql += " WHERE estado = :estado"
        params["estado"] = estado
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
        return [OrdenOut(**r) for r in rows]