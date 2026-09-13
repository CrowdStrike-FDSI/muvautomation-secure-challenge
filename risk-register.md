# 📋 Registro de Riesgos — Laboratorio 3

**Proyecto:** MuvAutomation Secure Challenge — caso Falcon Incident Hub
**Laboratorio:** 3 — Aplicación web pública por HTTP Red Team + Blue Team
**Equipo:** Oscar Andrés Sánchez Porras · Robinson Steven Núñez Portela
**Fecha de registro:** _completar_
**Tag de entrega:** `lab-3`

---

## 🎯 Propósito

Este documento registra los riesgos identificados durante el ciclo **Diseñar → Construir → Atacar → Detectar → Corregir → Verificar** del Laboratorio 3, clasificándolos según su estado de tratamiento y dejando explícitos los riesgos que se heredan al **Laboratorio 4**.

Límite explícito del Lab 3: la solución funciona por HTTP, sin TLS y sin identidad.

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
| R1 | Information Disclosure | El servidor expone la versión de Nginx en los headers de respuesta | `curl -I` antes/después — ver `evidence/retest/antes-headers-alertas.txt` (`Server: nginx/1.28.3 (Ubuntu)`) y `evidence/retest/despues-headers-alertas.txt` (`Server: nginx`) | Alta | Bajo | Media | ✅ Corregido | `server_tokens off;` aplicado en `nginx/muvautomation.conf`; verificado en retest (Fase F) |
| R2 | Information Disclosure | Ausencia de headers de seguridad (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) | Reporte ZAP pasivo (Fase C) + `curl -I` antes/después — ver `evidence/retest/antes-headers-alertas.txt` (sin headers) y `evidence/retest/despues-headers-alertas.txt` (3 headers presentes) | Alta | Bajo | Media | ✅ Corregido | Headers agregados en `nginx/muvautomation.conf`; verificado en retest (Fase F) |
| R3 | Elevation of Privilege / Tampering | Cualquier cliente del segmento puede crear o modificar alertas (`POST`/`PATCH /alertas`) sin autenticación, por el límite explícito del Lab 3 | `curl -X POST/PATCH` sin credenciales (pendiente — Fase C) | Alta | Alto | Alta | 🔵 Pendiente Lab 4 | Requiere autenticación/roles — fuera de alcance de Lab 3 |
| R4 | Information Disclosure | Enumeración de rutas de la API sin restricción (cualquier ruta se reenvía tal cual al backend) | Reconocimiento con `curl`/ZAP pasivo — completado en Fase C (nmap `-sT -sV`, fingerprinting de headers, exploración manual de endpoints) | Media | Bajo | Baja | ⚪ Aceptado | Se documenta como riesgo latente; no se restringe en Lab 3 |
| R5 | Information Disclosure | Contenido y payloads de alertas visibles en texto plano durante la captura de tráfico | PCAP filtrado (`tcpdump` + Wireshark, filtro `http`, streams 0–2) — ver `lab3-http-v2.pcap` y `evidence-lab3-http-plaintext.txt`; confirmado headers y body en claro (`GET /alertas`, `HTTP/1.1 200 OK`, `Content-Type: application/json`) | Alta | Medio | Alta | 🔵 Pendiente Lab 4 | Requiere TLS/HTTPS — fuera de alcance de este laboratorio |
| R6 | Tampering | Sin TLS, un intermediario podría alterar el tráfico en tránsito (no se ejecutó MITM real) | Ausencia de cifrado confirmada por inspección de tráfico (Wireshark, `lab3-http-v2.pcap`) | Baja (en lab controlado) | Alto | Media | 🔵 Pendiente Lab 4 | Se resolverá con certificados y HTTPS en el Laboratorio 4 |
| R7 | Repudiation | Sin autenticación ni identidad, no es posible atribuir una solicitud a un usuario específico | `evidence/blue/access.log` + `error.log`, correlacionados en `evidence/blue/correlacion-purple-team.md` (8 eventos Red Team↔log, ventana 13-sep 00:38–03:12 UTC). El log identifica IP y User-Agent, pero ninguna identidad real | Media | Medio | Media | 🔵 Pendiente Lab 4 | Requiere autenticación y control de identidad (Lab 4) |
| R8 | Denial of Service (potencial) | El servicio no limita la tasa de solicitudes por IP | Prueba conceptual, no ejecutada (regla del laboratorio prohíbe DoS) | Baja | Medio | Baja | ⚪ Aceptado | Fuera de alcance; se documenta como riesgo latente para revisión futura |
| R9 | Availability (limitación de diseño) | Las alertas se almacenan solo en memoria: se pierden al reiniciar el proceso de la API | Inspección del código (`app/main.py`); reforzado con evidencia en vivo en `error.log` (4× `connect() failed, Connection refused` hacia `127.0.0.1:8000` entre 03:06:55–03:08:37 UTC, backend caído/reiniciado durante las pruebas) | Alta (en cualquier reinicio) | Bajo | Baja | ⚪ Aceptado | Aceptado para Lab 3; una base de datos persistente queda como mejora futura |
| R10 | Elevation of Privilege | Ausencia total de control de acceso o roles en la aplicación (cualquier acción está disponible para cualquiera) | Inspección de la configuración del sitio y del backend | Alta | Alto | Alta | 🔵 Pendiente Lab 4 | Se resolverá al introducir autenticación y autorización por roles |
| R11 | Information Disclosure | `/docs` (Swagger UI) y `/openapi.json` accesibles sin autenticación, exponiendo el esquema completo de la API (los 4 endpoints, parámetros y modelos de datos) | Antes: `curl http://100.110.229.99/docs` y `/openapi.json` en 200 OK sin restricción — ver `evidence-lab3-http-plaintext.txt`, Wireshark (`tcp.stream eq 1` y `eq 2`), ZAP pasivo. Después: bloque `location` con `allow`/`deny` en Nginx — ver `evidence/retest/despues-docs-externo.txt` (403 sin autorización), `despues-docs-autorizado.txt` y `despues-openapi-autorizado.txt` (200 solo desde IPs en lista blanca) | Alta | Medio | Alta | 🟡 Mitigado | `location ~ ^/(docs\|openapi\.json) { allow ...; deny all; }` en `nginx/muvautomation.conf`, restringido a `LAB_CIDR` + IPs Tailscale fijas del equipo. Mitiga la exposición pública; no sustituye autenticación real (Lab 4) |

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
- Fase C (Red Team) completada: nmap confirmó `80/tcp open http nginx 1.28.3 (Ubuntu)`; fingerprinting con curl; hallazgo clave de `/docs` y `/openapi.json` expuestos (R11); ZAP pasivo exportado sin alertas propias de la API (solo recursos externos que carga Swagger UI).
- Fase D (captura de tráfico) completada: `tcpdump` en la interfaz `tailscale0` capturó 35 paquetes correspondientes a las 3 peticiones (`/alertas`, `/docs`, `/openapi.json`); Wireshark confirmó en los 3 streams HTTP (`tcp.stream eq 0, 1, 2`) que tanto los requests como las respuestas viajan en texto plano, sin ningún indicio de cifrado.
- Fase D (correlación de logs) completada: `access.log`/`error.log` revisados y correlacionados con 8 acciones del Red Team (ver `evidence/blue/correlacion-purple-team.md`). La ráfaga de escaneo `nmap -sT -sV` disparó la regla de ≥5×404 en 5 minutos. Se detectó además una caída no planeada del backend (4× `502`/`Connection refused`), que refuerza R9.
- Fase E (hardening) completada: se aplicó `server_tokens off`, headers de seguridad (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) y restricción por IP (`allow`/`deny`) sobre `/docs` y `/openapi.json` en `nginx/muvautomation.conf`. `sudo nginx -t` validó la sintaxis y `sudo systemctl reload nginx` aplicó los cambios sin downtime.
- Fase F (retest) completada para R1, R2 y R11 vía `curl` antes/después — ver `evidence/retest/`. Nota: el equipo opera principalmente vía Tailscale (rango `100.x.x.x`), no desde el segmento `192.168.15.0/24` original de Fase A; por eso la lista blanca de `/docs`/`/openapi.json` incluye tanto `LAB_CIDR` como las IPs Tailscale fijas del equipo. Pendiente: repetir `nmap`/`curl` de reconocimiento general (no solo headers) para consistencia con la evidencia Red Team de Fase C.

---

<div align="center">

**Secure Product Challenge · FDSI**
*Registro de riesgos — Laboratorio 3*

</div>
