# 📋 Registro de Riesgos — Laboratorio 3

**Proyecto:** MuvAutomation Secure Challenge
**Laboratorio:** 3 — Aplicación web pública por HTTP (Red Team + Blue Team)
**Equipo:** Oscar Andrés Sánchez Porras · Robinson Steven Núñez Portuela
**Fecha de registro:** _completar_
**Tag de entrega:** `lab-3`

---

## 🎯 Propósito

Este documento registra los riesgos identificados durante el ciclo **Diseñar → Construir → Atacar → Detectar → Corregir → Verificar** del Laboratorio 3, clasificándolos según su estado de tratamiento y dejando explícitos los riesgos que se heredan al **Laboratorio 4**.

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

| ID | Amenaza STRIDE | Descripción del riesgo | Evidencia | Severidad | Estado | Acción aplicada / planeada |
|---|---|---|---|---|---|---|
| R1 | Information Disclosure | El servidor expone la versión de Nginx en los headers de respuesta | `curl -I` antes del hardening | Media | ✅ Corregido | `server_tokens off;` — verificado en retest |
| R2 | Information Disclosure | Ausencia de headers de seguridad (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) | Reporte ZAP pasivo / `curl -I` | Media | ✅ Corregido | Headers agregados en bloque `server {}` de Nginx |
| R3 | Information Disclosure | Rutas y archivos ocultos (p. ej. `.git/config`) accesibles públicamente | `curl -i $TARGET_URL/.git/config` | Alta | ✅ Corregido | `location ~ /\. { deny all; }` — verificado en retest |
| R4 | Information Disclosure | Listado de directorios (`autoindex`) podría revelar archivos no enlazados | Inspección de configuración Nginx | Baja | 🟡 Mitigado | `autoindex off;` aplicado; persiste si se agregan nuevos archivos sin control |
| R5 | Information Disclosure | Contenido y rutas visibles en texto plano durante la captura de tráfico | PCAP filtrado (`tcpdump` + Wireshark, filtro `http`) | Alta | 🔵 Pendiente Lab 4 | Requiere TLS/HTTPS — fuera de alcance de este laboratorio |
| R6 | Tampering | Sin TLS, un intermediario podría alterar el tráfico en tránsito (no se ejecutó MITM real) | Ausencia de cifrado confirmada por inspección de tráfico | Alta | 🔵 Pendiente Lab 4 | Se resolverá con certificados y HTTPS en el Laboratorio 4 |
| R7 | Repudiation | Sin autenticación ni identidad, no es posible atribuir una solicitud a un usuario específico | Revisión de `access.log` | Media | 🔵 Pendiente Lab 4 | Requiere autenticación y control de identidad (Lab 4) |
| R8 | Denial of Service (potencial) | El servicio no limita la tasa de solicitudes por IP | Prueba conceptual, no ejecutada (regla de laboratorio prohíbe DoS) | Baja | ⚪ Aceptado | Fuera de alcance; se documenta como riesgo latente para revisión futura |
| R9 | Information Disclosure | El inventario público (`public-inventory.txt`) expone nombres de activos, aunque ficticios | Revisión manual del archivo | Baja | 🟡 Mitigado | Se redujo el contenido al mínimo necesario para la demostración |
| R10 | Elevation of Privilege (potencial) | Ausencia total de control de acceso o roles en la aplicación | Inspección de la configuración del sitio | Alta | 🔵 Pendiente Lab 4 | Se resolverá al introducir autenticación y autorización por roles |

---

## 🔎 Detalle de riesgos pendientes para el Laboratorio 4

| ID | Riesgo heredado | Por qué no se resuelve en Lab 3 |
|---|---|---|
| R5 | Confidencialidad del tráfico (sin TLS) | El Laboratorio 3 excluye deliberadamente HTTPS/certificados |
| R6 | Integridad del tráfico (Tampering) | Requiere TLS para garantizar integridad extremo a extremo |
| R7 | Trazabilidad de solicitudes (Repudiation) | Requiere identidad y autenticación, fuera de alcance |
| R10 | Control de acceso (Elevation of Privilege) | Requiere modelo de roles, introducido en Lab 4 |

---

## 🧾 Trazabilidad

Cada riesgo debe estar vinculado a:

1. **Hipótesis STRIDE** planteada en la Fase B.
2. **Comando o evidencia** que la validó (Fase C/D — `evidence/red/`, `evidence/blue/`).
3. **Corrección aplicada**, si corresponde (Fase E).
4. **Resultado del retest** (Fase F — `evidence/retest/`).

---

## 📝 Notas del equipo

- _Completar con observaciones adicionales, falsos positivos detectados en la regla de 404, o decisiones de alcance tomadas durante el laboratorio._

---

<div align="center">

**Secure Product Challenge · FDSI**
*Registro de riesgos — Laboratorio 3*

</div>