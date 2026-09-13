<div align="center">

# 🛡️ MuvAutomation Secure Challenge

### Laboratorio 3 — Red Team + Blue Team

**Aplicación web pública por HTTP: construir, atacar, detectar, corregir y verificar**

![Status](https://img.shields.io/badge/estado-en%20progreso-yellow)
![Modo](https://img.shields.io/badge/modo-acad%C3%A9mico-blue)
![Protocolo](https://img.shields.io/badge/protocolo-HTTP-orange)
![Servidor](https://img.shields.io/badge/servidor-Nginx-009639?logo=nginx&logoColor=white)
![Licencia](https://img.shields.io/badge/uso-autorizado-lightgrey)

</div>

---

## 👥 Equipo

| Rol | Integrante |
|---|---|
| Estudiante | **Oscar Andrés Sánchez Porras** |
| Estudiante | **Robinson Steven Núñez Portela** |

---

## 📌 Descripción del proyecto

Este repositorio contiene la solución del **Laboratorio 3** del reto *Secure Product Challenge (FDSI)*, cuyo objetivo es establecer una **línea base deliberadamente insegura y controlada**: una aplicación web mínima publicada por **HTTP, sin autenticación ni cifrado**, sobre la cual se ejecuta un ciclo completo de trabajo ofensivo/defensivo:

<div align="center">

**Diseñar → Construir → Atacar → Detectar → Corregir → Verificar**

</div>

**Caso asignado: Falcon Incident Hub.** En vez de un sitio estático genérico, la aplicación es un prototipo que recibe alertas ficticias de CrowdStrike Falcon, permite consultarlas mediante una API y registra las acciones tomadas sobre ellas (host, identidad, indicadores). No se usa información real ni se integra directamente con CrowdStrike.

Este laboratorio es la **base acumulativa** sobre la que se construirán los siguientes retos del programa (HTTPS, identidad y roles, DevSecOps, y Cloud Purple Team).

> ⚠️ **Uso exclusivamente académico.** Todas las pruebas se ejecutan únicamente contra la IP/URL asignada al equipo, dentro de la ventana autorizada, usando datos, cuentas y tokens ficticios.

---

## 🎯 Objetivos

- 🚀 Desplegar una aplicación web mínima en una instancia Linux autorizada.
- 🔍 Identificar la superficie de ataque con **Nmap**, **curl** y **OWASP ZAP** (modo pasivo).
- 📡 Evidenciar por qué HTTP expone metadatos y contenido en tránsito.
- 🧩 Relacionar hallazgos con amenazas **STRIDE**, en especial *Information Disclosure* y *Tampering*.
- 🧾 Analizar `access.log` / `error.log` desde una perspectiva Blue Team.
- 🔧 Aplicar hardening inicial (sin adelantar autenticación ni HTTPS, reservados para el Laboratorio 4).
- 🤖 Usar IA de forma responsable, sobre evidencia anonimizada.

---

## 🏗️ Arquitectura y modelo de amenazas

Diagrama de arquitectura del ejercicio (topología Kali → Nginx → API de Alertas) y DFD ligero con los dos límites de confianza (tránsito de red a servidor, y proxy a aplicación):

![Arquitectura del Laboratorio 3](docs/00-diagramas/01-arquitectura-lab3.png)

![DFD con límites de confianza](docs/00-diagramas/02-dfd-lab3.png)

```
Adversary / Red Team (Kali)
          │  HTTP :80, texto claro
          ▼
    Nginx (reverse proxy, sin autenticación)
          │  proxy_pass → 127.0.0.1:8000
          ▼
  API de Alertas (FastAPI) — Falcon Incident Hub
   ListAlerts / RegisterAlert / UpdateAlertStatus / DescribeAlert
          │
          ▼
  Memoria (alertas simuladas + acciones registradas)
          │
          ▼
  Logs + PCAP (Blue Team, visibilidad parcial en Lab 3)
```

| Componente | Función | Evidencia esperada |
|---|---|---|
| 🐉 Kali Linux | Reconocimiento y validación autorizada | Comandos, timestamps, capturas, reporte ZAP |
| 🖥️ Ubuntu Server LTS | Host de la aplicación | Estado del servicio, firewall, configuración, logs |
| 🌐 Nginx (reverse proxy) | Enruta HTTP :80 hacia el backend, sin autenticación | Respuesta HTTP, headers, `nginx/muvautomation.conf` |
| 🧠 FastAPI (`app/main.py`) | API de Alertas — Falcon Incident Hub, datos en memoria | Respuestas JSON de `/alertas` |
| 📶 tcpdump / Wireshark | Visibilidad de red | PCAP filtrado del ejercicio |
| 📄 access.log / error.log | Telemetría defensiva | Eventos correlacionados con pruebas Red Team |
| 🤖 IA autorizada / offline | Apoyo analítico opcional | Prompt anonimizado y validación humana |

---

## 📂 Estructura del repositorio

> `app/` y `reports/zap-passive/` ya están cargados en GitHub y no se incluyen en este paquete.

```
muvautomation-secure-challenge/
├── app/                       # Backend FastAPI (ya en GitHub)
├── nginx/
│   └── muvautomation.conf     # Virtual host: reverse proxy hacia 127.0.0.1:8000
├── diagrams/
│   └── dfd-lab3.png           # Diagrama de flujo de datos (DFD), 2 límites de confianza
├── docs/                      # Capturas organizadas por fase (este entregable)
│   ├── 00-diagramas/
│   ├── 01-fase-a-construccion/
│   ├── 02-fase-b-modelado/
│   ├── 03-fase-c-red-team/
│   ├── 04-fase-d-blue-team/
│   └── 05-wireshark/
├── evidence/
│   ├── red/                   # Nmap, curl, reporte ZAP pasivo
│   └── blue/                  # Logs, PCAP, evidencia de tráfico en claro
├── reports/
│   └── zap-passive/           # Reporte HTML de OWASP ZAP (ya en GitHub)
├── risk-register.md           # Registro de riesgos (corregido/mitigado/aceptado/pendiente)
└── README.md
```

---

## ⚙️ Variables de entorno

```bash
export TARGET_IP=IP_ASIGNADA
export TARGET_URL=http://$TARGET_IP
export LAB_CIDR=CIDR_AUTORIZADO
```

**Valores usados en esta ejecución** (host Ubuntu conectado por Tailscale):

```bash
export TARGET_IP=100.110.229.99
export TARGET_URL=http://$TARGET_IP
```

> El host se publicó inicialmente en una red NAT local (`192.168.15.0/24`) para la Fase A, y se validó de forma remota vía Tailscale (`100.110.229.99`) para las Fases C y D.

---

## 🧪 Ciclo de trabajo

| Fase | Actividad | Responsable | Estado |
|---|---|---|---|
| A | Construcción y publicación HTTP (Ubuntu, Nginx, backend, firewall) | Builder | ✅ Completa |
| B | DFD ligero + hipótesis STRIDE + matriz de riesgos | Todo el equipo | ✅ Completa |
| C | Reconocimiento y pruebas ofensivas | Red Team | ✅ Completa |
| D | Correlación de logs y detección | Blue Team | 🔵 En curso (captura de tráfico completada; falta revisión de `access.log`) |
| E | Hardening inicial de Nginx | Blue Team | 🔵 Pendiente |
| F | Retest y comparación antes/después | Purple Team | 🔵 Pendiente |

### 🟢 Construcción (Fase A)

- Host Ubuntu 24.04.1 LTS verificado (`hostnamectl`, `ip -br address`) antes de instalar cualquier servicio.
- Nginx instalado, habilitado y validado escuchando en el puerto 80.
- Backend FastAPI (`app/main.py`) con los 4 endpoints de la API de Alertas, corriendo en `127.0.0.1:8000` y probado localmente antes de exponerlo.
- Virtual host de Nginx configurado como reverse proxy, y firewall (`ufw`) restringido al segmento del laboratorio (`192.168.15.0/24`).
- Prueba de acceso externo confirmada desde un navegador fuera del host.

![Backend FastAPI — main.py con los 4 endpoints de la API](docs/01-fase-a-construccion/04-backend-main-py-code.png)

![Firewall ufw restringido al segmento del laboratorio](docs/01-fase-a-construccion/07-firewall-ufw-status.png)

### 🔴 Hallazgos clave (Red Team)

- `nmap -sT -sV` confirmó `80/tcp open http nginx 1.28.3 (Ubuntu)`.
- `/docs` (Swagger UI) y `/openapi.json` accesibles **sin autenticación**, exponiendo los 4 endpoints de la API (`GET/POST /alertas`, `GET/PATCH /alertas/{alert_id}`) y el esquema completo de datos (**R11**).
- ZAP pasivo detectó 11 alertas (CSP ausente, Cross-Domain Misconfiguration, Anti-clickjacking Header, Sub Resource Integrity), todas de baja severidad y en su mayoría sobre recursos externos que carga Swagger UI.
- Rutas no existentes (`/`, `/admin`, `/alertas/1`) responden `404 Not Found`, sin filtrar información adicional.

![Nmap -sT (puerto abierto) y curl de cabeceras](docs/03-fase-c-red-team/02-nmap-sT-open-curl-headers.png)

![/docs — Swagger UI expone los 4 endpoints de la API](docs/03-fase-c-red-team/08-docs-swagger-endpoints-expuestos.png)

![ZAP — panel de alertas pasivas (11 hallazgos)](docs/03-fase-c-red-team/15-zap-alerts-panel.png)

### 🔵 Detección (Blue Team)

- Captura de tráfico completada con `tcpdump` sobre la interfaz `tailscale0`: 35 paquetes correspondientes a las peticiones a `/alertas`, `/docs` y `/openapi.json`.
- `/openapi.json` confirma en texto plano el esquema completo de la API (modelos `Alert`, `HTTPValidationError`), reforzando el hallazgo R11.
- Evidencia (PCAP + volcado de texto) descargada del servidor hacia el equipo de análisis vía `scp`.
- Pendiente: correlación con `access.log` / `error.log` para R7 (Repudiation).

![curl a /openapi.json — esquema completo de la API en texto plano](docs/04-fase-d-blue-team/02-curl-openapi-json.png)

![Descarga de evidencia (PCAP y volcado de texto) vía scp](docs/04-fase-d-blue-team/03-scp-descarga-pcap-y-evidencia.png)

### 📡 Evidencia de tráfico en claro (Wireshark)

Los tres streams HTTP capturados (`tcp.stream eq 0, 1, 2`) confirman que tanto las peticiones como las respuestas —incluyendo el cuerpo JSON completo— viajan **sin cifrar**:

![Stream 0 — GET /alertas](docs/05-wireshark/01-tcp-stream-0-get-alertas.png)

![Stream 1 — GET /docs](docs/05-wireshark/02-tcp-stream-1-get-docs.png)

![Stream 2 — GET /openapi.json](docs/05-wireshark/03-tcp-stream-2-get-openapi-json.png)

### 🛠️ Hardening planeado (aún no aplicado)
```nginx
server_tokens off;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "no-referrer" always;
autoindex off;
location ~ ^/(docs|openapi\.json) { deny all; }
```

> 🔓 **Límite pedagógico:** HTTP sigue siendo inseguro en confidencialidad e integridad, y la API no tiene autenticación. Estos riesgos quedan abiertos intencionalmente para el **Laboratorio 4** (HTTPS, identidad, sesiones y roles).

---

## 🧵 Amenazas STRIDE identificadas

| ID | STRIDE | Hipótesis | Validación |
|---|---|---|---|
| H1 | Information Disclosure | HTTP permite observar contenido y rutas en tránsito (payloads de alertas incluidos) | PCAP filtrado |
| H2 | Information Disclosure | Headers y respuestas revelan tecnología/recursos (Nginx/FastAPI) | `curl -I` + ZAP pasivo |
| H3 | Repudiation | Sin correlación temporal ni identidad, no se atribuyen solicitudes a un origen | Comparación con `access.log` |
| H4 | Tampering | Sin TLS, tráfico potencialmente alterable (no se ejecuta MITM real) | Evidencia de ausencia de protección |
| H5 | Elevation of Privilege / Tampering | Cualquiera en el segmento puede crear/modificar alertas vía `RegisterAlert`/`UpdateAlertStatus` sin autenticación | `curl -X POST/PATCH` sin credenciales desde Kali |

Ver el detalle de riesgos, severidades y estado de tratamiento en [`risk-register.md`](risk-register.md).

---

## 📸 Evidencia adicional por fase

La carpeta [`docs/`](docs/) contiene todas las capturas del laboratorio organizadas por fase:

- **`docs/00-diagramas/`** — arquitectura y DFD.
- **`docs/01-fase-a-construccion/`** — línea base del host (`hostnamectl`, `ip -br address`), instalación de Nginx, entorno virtual y código del backend FastAPI, prueba local con `curl`, configuración del reverse proxy, firewall `ufw` y prueba de acceso desde un navegador externo.
- **`docs/02-fase-b-modelado/`** — verificación de red del atacante (`ip a`), estado de Tailscale y prueba de conectividad (`curl` + `ping`) contra el objetivo.
- **`docs/03-fase-c-red-team/`** — reconocimiento con Nmap (`-sS` filtrado y `-sT -sV` confirmado), `curl` de cabeceras y contenido, exploración pasiva con OWASP ZAP (Manual Explore, árbol de sitios, panel de alertas) y verificación manual de rutas (`/`, `/admin`, `/alertas/1`, `/docs`).
- **`docs/04-fase-d-blue-team/`** — consulta de `/docs` y `/openapi.json`, y descarga de la evidencia de tráfico (`lab3-http-v2.pcap` y volcado de texto) hacia el equipo de análisis.
- **`docs/05-wireshark/`** — los 3 streams HTTP analizados en Wireshark.

---

## 🤖 Uso responsable de IA

La IA se emplea como **copiloto analítico**, nunca como autoridad. Todo hallazgo se valida contra comandos, logs, PCAP o configuración real. No se comparten IP reales, PCAP completos ni datos sensibles; toda evidencia se anonimiza antes de su uso.

---

## ✅ Checklist de cierre

- [ ] IP objetivo autorizada por el docente
- [x] Sin datos reales en el contenido (alertas simuladas)
- [x] Servicio HTTP accesible desde el segmento permitido
- [x] Comandos y timestamps conservados (Red Team)
- [ ] Mínimo 3 eventos correlacionados (Blue Team) — falta revisión de `access.log`
- [x] PCAP limitado al tráfico del laboratorio
- [ ] Headers de seguridad y reducción de exposición aplicados (Fase E)
- [ ] Retest ejecutado (Fase F)
- [x] Riesgos pendientes documentados para el Laboratorio 4
- [ ] Tag `lab-3` publicado
- [ ] Reflexión individual (máx. 250 palabras)

---

## 📝 Qué falta para cerrar el laboratorio

1. **Fase D:** revisar `access.log` / `error.log` y correlacionar al menos 3 eventos con las pruebas del Red Team (R7).
2. **Fase E:** aplicar el hardening de Nginx (`server_tokens off`, headers de seguridad, bloqueo de `/docs` y `/openapi.json`) y capturar evidencia antes/después.
3. **Fase F:** repetir `nmap`/`curl` tras el hardening y documentar la comparación (`evidence/retest/`).
4. Redactar la reflexión individual (máx. 250 palabras) y completar la fecha de registro en `risk-register.md`.
5. Confirmar la IP autorizada por el docente y publicar el tag `lab-3`.

<div align="center">

**Secure Product Challenge · FDSI**
*Laboratorio 3 — Red Team + Blue Team · Uso académico autorizado*

</div>
