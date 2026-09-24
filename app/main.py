"""
Falcon Incident Hub - API de Alertas
Laboratorio 3 - Parte 2: autenticacion JWT + roles + log de auditoria.

Resuelve del risk-register.md (Lab 3):
  - R3 (Elevation of Privilege / Tampering): POST/PATCH ahora requieren
    token JWT valido con rol "analyst".
  - R7 (Repudiation): cada accion de escritura queda asociada al usuario
    real (del token), no solo a una IP, via audit_log en memoria.
  - R10 (Elevation of Privilege): control de acceso por rol
    (viewer = solo lectura, analyst = lectura + escritura).

Nota pedagogica: usuarios y SECRET_KEY estan hardcodeados para el
laboratorio academico. En produccion, SECRET_KEY debe venir de una
variable de entorno / secret manager, y los usuarios de una base de
datos con hashes unicos por despliegue.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# --- Configuracion JWT ---
# En produccion: mover a variable de entorno (os.environ["SECRET_KEY"])
SECRET_KEY = "lab3-parte2-falcon-incident-hub-CAMBIAR-EN-PRODUCCION-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Falcon Incident Hub - API de Alertas")


# --- Usuarios demo (Lab 3 - Parte 2: reemplazar por BD real en Lab 5/produccion) ---
# Contrasenas de ejemplo: "viewer123" y "analyst123"
fake_users_db = {
    "oscar": {
        "username": "oscar",
        "role": "analyst",
        "hashed_password": pwd_context.hash("analyst123"),
    },
    "robinson": {
        "username": "robinson",
        "role": "analyst",
        "hashed_password": pwd_context.hash("analyst123"),
    },
    "auditor": {
        "username": "auditor",
        "role": "viewer",
        "hashed_password": pwd_context.hash("viewer123"),
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class User(BaseModel):
    username: str
    role: str


class Alert(BaseModel):
    id: int
    host: str
    severity: str            # low | medium | high | critical
    indicator_type: str      # ej: malware, lateral_movement, exfiltration
    status: str = "open"     # open | investigating | closed
    action_taken: Optional[str] = None


class AuditEntry(BaseModel):
    timestamp: str
    username: str
    role: str
    action: str
    detail: str


alerts: List[Alert] = []
audit_log: List[AuditEntry] = []


# --- Utilidades de autenticacion ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    user = fake_users_db.get(username)
    if user:
        return user
    return None


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def log_action(user: User, action: str, detail: str):
    audit_log.append(
        AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            username=user.username,
            role=user.role,
            action=action,
            detail=detail,
        )
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(username=user["username"], role=user["role"])


def require_analyst(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "analyst":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol 'analyst' para esta accion",
        )
    return current_user


# --- Endpoint de login ---
@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Endpoints de alertas (protegidos) ---
@app.get("/alertas")
def list_alerts(current_user: User = Depends(get_current_user)):
    return alerts


@app.post("/alertas")
def register_alert(alert: Alert, current_user: User = Depends(require_analyst)):
    alerts.append(alert)
    log_action(current_user, "register_alert", f"alert_id={alert.id}")
    return alert


@app.get("/alertas/{alert_id}")
def describe_alert(alert_id: int, current_user: User = Depends(get_current_user)):
    for a in alerts:
        if a.id == alert_id:
            return a
    raise HTTPException(status_code=404, detail="Alerta no encontrada")


@app.patch("/alertas/{alert_id}")
def update_alert_status(
    alert_id: int,
    status: str,
    action_taken: Optional[str] = None,
    current_user: User = Depends(require_analyst),
):
    for a in alerts:
        if a.id == alert_id:
            a.status = status
            if action_taken:
                a.action_taken = action_taken
            log_action(
                current_user,
                "update_alert_status",
                f"alert_id={alert_id} status={status}",
            )
            return a
    raise HTTPException(status_code=404, detail="Alerta no encontrada")


# --- Auditoria (solo analyst, resuelve R7 con evidencia consultable) ---
@app.get("/audit", response_model=List[AuditEntry])
def get_audit_log(current_user: User = Depends(require_analyst)):
    return audit_log
