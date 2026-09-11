from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Falcon Incident Hub - API de Alertas")


class Alert(BaseModel):
    id: int
    host: str
    severity: str            # low | medium | high | critical
    indicator_type: str      # ej: malware, lateral_movement, exfiltration
    status: str = "open"     # open | investigating | closed
    action_taken: Optional[str] = None


alerts: List[Alert] = []


@app.get("/alertas")
def list_alerts():
    return alerts


@app.post("/alertas")
def register_alert(alert: Alert):
    alerts.append(alert)
    return alert


@app.get("/alertas/{alert_id}")
def describe_alert(alert_id: int):
    for a in alerts:
        if a.id == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alerta no encontrada")


@app.patch("/alertas/{alert_id}")
def update_alert_status(alert_id: int, status: str, action_taken: Optional[str] = None):
    for a in alerts:
        if a.id == alert_id:
            a.status = status
            if action_taken:
                a.action_taken = action_taken
            return a
    raise HTTPException(status_code=404, detail="Alerta no encontrada")
