# 📋 Registro de Riesgos — Laboratorio 3

**Proyecto:** MuvAutomation Secure Challenge — caso Falcon Incident Hub
**Laboratorio:** 3 — Aplicación web pública por HTTP (Red Team + Blue Team)
**Equipo:** Oscar Andrés Sánchez Porras · Robinson Steven Núñez Portela
**Fecha de registro:** _completar_
**Tag de entrega:** `lab-3`

---

## 🎯 Propósito

Este documento registra los riesgos identificados durante el ciclo **Diseñar → Construir → Atacar → Detectar → Corregir → Verificar** del Laboratorio 3, clasificándolos según su estado de tratamiento y dejando explícitos los riesgos que se heredan al **Laboratorio 4**.

Límite explícito del Lab 3 (definido por el profesor): la solución funciona por HTTP, sin TLS y sin identidad.

---

## 🏷️ Estados posibles

| Estado | Significado |
|---|---|
| ✅ **Corregido** | La causa raíz fue eliminada y verificada en el retest. |
| 🟡 **Mitigado** | Se redujo la probabilidad o el impacto, pero el riesgo de fondo persiste. |
| ⚪ **Aceptado** | El equipo decide no tratarlo en este laboratorio, con justificación explícita. |
| 🔵 **Pendiente Lab 4** | Riesgo fuera de alcance de este laboratorio; se resolverá con HTTPS, identidad, sesiones y roles. |

---

## 📊 Tabla de riesgos

| ID | Amenaza STRIDE | Descripción del riesgo | Evidencia | Probabilidad | Impacto | Severidad | Estado | Acción aplicada / planeada |
|---|---|---|---|---|---|---|---|---|
| R1 | Information Disclosure | El servidor expone la versión de Nginx en los headers de respuesta | `curl -I` (pendiente de capturar antes/después del hardening) | Alta | Bajo | Media | 🔵 Pendiente (Fase E) | `server_tokens off;` — a verificar en retest |
| R2 | Information Disclosure | Ausencia de headers de seguridad (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) | Reporte ZAP pasivo / `curl -I` (pendiente — Fase C) | Alta | Bajo | Media | 🔵 Pendiente (Fase E) | Headers a agregar en `nginx/muvautomation.conf` |
| R3 | Elevation of Privilege / Tampering | Cualquier cliente del segmento puede crear o modificar alertas (`POST`/`PATCH /alertas`) sin autenticación, por el límite explícito del Lab 3 | `curl -X POST/PATCH` sin credenciales (pendiente — Fase C) | Alta | Alto | Alta | 🔵 Pendiente Lab 4 | Requiere autenticación/roles — fuera de alcance de Lab 3 |
| R4 | Information Disclosure | Enumeración de rutas de la API sin restricción (cualquier ruta se reenvía tal cual al backend) | Reconocimiento con `curl`/ZAP pasivo (pendiente — Fase C) | Media | Bajo | Baja | ⚪ Aceptado | Se documenta como riesgo latente; no se restringe en Lab 3 |
| R5 | Information Disclosure | Contenido y payloads de alertas visibles en texto plano durante la captura de tráfico | PCAP filtrado (`tcpdump` + Wireshark, filtro `http`) (pendiente — Fase D) | Alta | Medio | Alta | 🔵 Pendiente Lab 4 | Requiere TLS/HTTPS — fuera de alcance de este laboratorio |
| R6 | Tampering | Sin TLS, un intermediario podría alterar el tráfico en tránsito (no se ejecutó MITM real) | Ausencia de cifrado confirmada por inspección de tráfico (pendiente — Fase D) | Baja (en lab controlado) | Alto | Media | 🔵 Pendiente Lab 4 | Se resolverá con certificados y HTTPS en el Laboratorio 4 |
| R7 | Repudiation | Sin autenticación ni identidad, no es posible atribuir una solicitud a un usuario específico | Revisión de `access.log` (pendiente — Fase D) | Media | Medio | Media | 🔵 Pendiente Lab 4 | Requiere autenticación y control de identidad (Lab 4) |
| R8 | Denial of Service (potencial) | El servicio no limita la tasa de solicitudes por IP | Prueba conceptual, no ejecutada (regla del laboratorio prohíbe DoS) | Baja | Medio | Baja | ⚪ Aceptado | Fuera de alcance; se documenta como riesgo latente para revisión futura |
| R9 | Availability (limitación de diseño) | Las alertas se almacenan solo en memoria: se pierden al reiniciar el proceso de la API | Inspección del código (`app/main.py`) | Alta (en cualquier reinicio) | Bajo | Baja | ⚪ Aceptado | Aceptado para Lab 3; una base de datos persistente queda como mejora futura |
| R10 | Elevation of Privilege | Ausencia total de control de acceso o roles en la aplicación (cualquier acción está disponible para cualquiera) | Inspección de la configuración del sitio y del backend | Alta | Alto | Alta | 🔵 Pendiente Lab 4 | Se resolverá al introducir autenticación y autorización por roles |

---

## 🔎 Detalle de riesgos pendientes para el Laboratorio 4

| ID | Riesgo heredado | Por qué no se resuelve en Lab 3 |
|---|---|---|
| R3 | Escritura no autenticada en la API de alertas | Requiere identidad y control de acceso, fuera de alcance |
| R5 | Confidencialidad del tráfico (sin TLS) | El Laboratorio 3 excluye deliberadamente HTTPS/certificados |
| R6 | Integridad del tráfico (Tampering) | Requiere TLS para garantizar integridad extremo a extremo |
| R7 | Trazabilidad de solicitudes (Repudiation) | Requiere identidad y autenticación, fuera de alcance |
| R10 | Control de acceso (Elevation of Privilege) | Requiere modelo de roles, introducido en Lab 4 |

---

## 🧾 Trazabilidad

Cada riesgo debe estar vinculado a:

1. **Hipótesis STRIDE** planteada en la Fase B (ver `README.md`, sección "Amenazas STRIDE").
2. **Comando o evidencia** que la validó (Fase C/D — `evidence/red/`, `evidence/blue/`; evidencia de construcción en `evidence/build/`).
3. **Corrección aplicada**, si corresponde (Fase E).
4. **Resultado del retest** (Fase F — `evidence/retest/`).

---

## 📝 Notas del equipo

- El caso asignado (Falcon Incident Hub) reemplaza el sitio estático genérico de la guía base por una API de alertas (FastAPI) detrás de un reverse proxy Nginx. Esto elimina riesgos propios de sitios estáticos (listados de directorio, archivos ocultos tipo `.git/`) pero introduce el riesgo específico de escritura no autenticada (R3), que no existía en la versión genérica.
- Las filas marcadas "pendiente — Fase C/D" se completarán con evidencia real en cuanto la VM de Kali esté lista y se ejecute el reconocimiento y la correlación de logs.

---

<div align="center">

**Secure Product Challenge · FDSI**
*Registro de riesgos — Laboratorio 3*

</div>
