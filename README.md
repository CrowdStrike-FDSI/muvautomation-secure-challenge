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

## 🏗️ Arquitectura del ejercicio

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

Diagrama completo con límites de confianza en `diagrams/dfd-lab3.png`.

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

```
muvautomation-secure-challenge/
├── app/
│   └── main.py              # Backend FastAPI — API de Alertas (Falcon Incident Hub)
├── nginx/
│   └── muvautomation.conf   # Virtual host: reverse proxy hacia 127.0.0.1:8000
├── diagrams/
│   └── dfd-lab3.png         # Diagrama de flujo de datos (DFD), 2 límites de confianza
├── evidence/
│   ├── build/                # Evidencia de la Fase A (línea base, nginx, backend, firewall)
│   ├── red/                  # Nmap, curl, reporte ZAP pasivo (pendiente — Fase C)
│   └── blue/                 # Logs, PCAP, regla de detección (pendiente — Fase D)
├── reports/
│   └── zap-passive/          # Reporte HTML de OWASP ZAP (pendiente — Fase C)
├── risk-register.md          # Registro de riesgos (corregido/mitigado/aceptado/pendiente)
└── README.md
```

---

## ⚙️ Variables de entorno

```bash
export TARGET_IP=IP_ASIGNADA
export TARGET_URL=http://$TARGET_IP
export LAB_CIDR=CIDR_AUTORIZADO
```

**Valores usados en esta ejecución** (VM local en VMware, red NAT — no hay IP asignada por el docente):

```bash
export TARGET_IP=192.168.15.132
export LAB_CIDR=192.168.15.0/24
```

> Con NAT de VMware la IP puede cambiar si la VM se mueve de equipo. Verificar siempre con `ip -br address` antes de las pruebas.

---

## 🧪 Ciclo de trabajo

| Fase | Actividad | Responsable | Estado |
|---|---|---|---|
| A | Construcción y publicación HTTP (Ubuntu, Nginx, backend, firewall) | Builder | ✅ Completa |
| B | DFD ligero + hipótesis STRIDE + matriz de riesgos | Todo el equipo | ✅ Completa |
| C | Reconocimiento y pruebas ofensivas | Red Team | 🔵 Pendiente (a la espera de la VM de Kali) |
| D | Correlación de logs y detección | Blue Team | 🔵 Pendiente |
| E | Hardening inicial de Nginx | Blue Team | 🔵 Pendiente |
| F | Retest y comparación antes/después | Purple Team | 🔵 Pendiente |

### 🔴 Hallazgos clave (Red Team)
_Pendiente — se completa al ejecutar la Fase C con Kali (nmap, curl, ZAP pasivo contra `$TARGET_URL/alertas`)._

### 🔵 Detección (Blue Team)
_Pendiente — se completa al ejecutar la Fase D (correlación de `access.log`, regla de ≥5 respuestas 404 en 5 min, captura `tcpdump`)._

### 🛠️ Hardening planeado (aún no aplicado)
```nginx
server_tokens off;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "no-referrer" always;
autoindex off;
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

---

## 🤖 Uso responsable de IA

La IA se emplea como **copiloto analítico**, nunca como autoridad. Todo hallazgo se valida contra comandos, logs, PCAP o configuración real. No se comparten IP reales, PCAP completos ni datos sensibles; toda evidencia se anonimiza antes de su uso.

---

## ✅ Checklist de cierre

- [ ] IP objetivo autorizada
- [x] Sin datos reales en el contenido (alertas simuladas)
- [x] Servicio HTTP accesible desde el segmento permitido
- [ ] Comandos y timestamps conservados (Red Team)
- [ ] Mínimo 3 eventos correlacionados (Blue Team)
- [ ] PCAP limitado al tráfico del laboratorio
- [ ] Headers de seguridad y reducción de exposición aplicados
- [ ] Retest ejecutado
- [x] Riesgos pendientes documentados para el Laboratorio 4
- [ ] Tag `lab-3` publicado

---

<div align="center">

**Secure Product Challenge · FDSI**
*Laboratorio 3 — Red Team + Blue Team · Uso académico autorizado*

</div>
