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
| Estudiante | **Robinson Steven Núñez Portuela** |

---

## 📌 Descripción del proyecto

Este repositorio contiene la solución del **Laboratorio 3** del reto *Secure Product Challenge (FDSI)*, cuyo objetivo es establecer una **línea base deliberadamente insegura y controlada**: una aplicación web mínima publicada por **HTTP, sin autenticación ni cifrado**, sobre la cual se ejecuta un ciclo completo de trabajo ofensivo/defensivo:

<div align="center">

**Diseñar → Construir → Atacar → Detectar → Corregir → Verificar**

</div>

Este laboratorio es la **base acumulativa** sobre la que se construirán los siguientes retos del programa (HTTPS, identidad y roles, DevSecOps, y Cloud Purple Team).

> ⚠️ **Uso exclusivamente académico.** Todas las pruebas se ejecutan únicamente contra la IP/URL asignada por el docente, dentro de la ventana autorizada, usando datos, cuentas y tokens ficticios.

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
Usuario / Kali Linux (Red Team)
          │
          ▼
   Red del laboratorio
          │
          ▼
    Nginx :80 (HTTP)
          │
          ▼
  Sitio estático MuvAutomation
          │
          ▼
  Logs + PCAP (Blue Team)
```

| Componente | Función | Evidencia esperada |
|---|---|---|
| 🐉 Kali Linux | Reconocimiento y validación autorizada | Comandos, timestamps, capturas, reporte ZAP |
| 🖥️ Ubuntu Server LTS | Host de la aplicación | Estado del servicio, firewall, configuración, logs |
| 🌐 Nginx + sitio estático | Servicio HTTP sin autenticación | Respuesta HTTP, headers, recursos públicos |
| 📶 tcpdump / Wireshark | Visibilidad de red | PCAP filtrado del ejercicio |
| 📄 access.log / error.log | Telemetría defensiva | Eventos correlacionados con pruebas Red Team |
| 🤖 IA autorizada / offline | Apoyo analítico opcional | Prompt anonimizado y validación humana |

---

## 📂 Estructura del repositorio

```
muvautomation-secure-challenge/
├── app/                     # Sitio estático (index.html, public-inventory.txt)
├── nginx/                   # Configuración del virtual host
├── diagrams/
│   └── dfd-lab3.png         # Diagrama de flujo de datos (DFD)
├── evidence/
│   ├── red/                 # Nmap, curl, reporte ZAP pasivo
│   └── blue/                # Logs, PCAP, regla de detección
├── reports/
│   └── zap-passive/         # Reporte HTML de OWASP ZAP
├── risk-register.md         # Registro de riesgos (corregido/mitigado/aceptado/pendiente)
└── README.md
```

---

## ⚙️ Variables de entorno

```bash
export TARGET_IP=IP_ASIGNADA
export TARGET_URL=http://$TARGET_IP
export LAB_CIDR=CIDR_AUTORIZADO
```

---

## 🧪 Ciclo de trabajo

| Fase | Actividad | Responsable |
|---|---|---|
| A | Construcción y publicación HTTP | Builder |
| B | DFD ligero + hipótesis STRIDE | Todo el equipo |
| C | Reconocimiento y pruebas ofensivas | Red Team |
| D | Correlación de logs y detección | Blue Team |
| E | Hardening inicial de Nginx | Blue Team |
| F | Retest y comparación antes/después | Purple Team |

### 🔴 Hallazgos clave (Red Team)
- Puerto **80/TCP** abierto, servicio identificado por Nmap.
- Headers y contenido visibles en texto plano (sin TLS).
- Archivo público `public-inventory.txt` accesible sin restricciones.

### 🔵 Detección (Blue Team)
- Correlación de IP, timestamp, método, ruta y status code en `access.log`.
- Regla de laboratorio: **≥ 5 respuestas 404 de una misma IP en 5 minutos**.
- Captura de tráfico limitada (`tcpdump`) y análisis con Wireshark (`filtro http`).

### 🛠️ Hardening aplicado
```nginx
server_tokens off;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "no-referrer" always;
autoindex off;
location ~ /\. { deny all; }
```

> 🔓 **Límite pedagógico:** HTTP sigue siendo inseguro en confidencialidad e integridad. Este riesgo queda abierto intencionalmente para el **Laboratorio 4** (HTTPS, identidad, sesiones y roles).

---

## 🧵 Amenazas STRIDE identificadas

| ID | STRIDE | Hipótesis | Validación |
|---|---|---|---|
| H1 | Information Disclosure | HTTP permite observar contenido y rutas en tránsito | PCAP filtrado |
| H2 | Information Disclosure | Headers y respuestas revelan tecnología/recursos | `curl -I` + ZAP pasivo |
| H3 | Repudiation | Sin correlación temporal no se atribuyen solicitudes | Comparación con `access.log` |
| H4 | Tampering | Sin TLS, tráfico potencialmente alterable (no se ejecuta MITM) | Evidencia de ausencia de protección |

---

## 🤖 Uso responsable de IA

La IA se emplea como **copiloto analítico**, nunca como autoridad. Todo hallazgo se valida contra comandos, logs, PCAP o configuración real. No se comparten IP reales, PCAP completos ni datos sensibles; toda evidencia se anonimiza antes de su uso.

---

## ✅ Checklist de cierre

- [ ] IP objetivo autorizada
- [ ] Sin datos reales en el contenido
- [ ] Servicio HTTP accesible desde el segmento permitido
- [ ] Comandos y timestamps conservados (Red Team)
- [ ] Mínimo 3 eventos correlacionados (Blue Team)
- [ ] PCAP limitado al tráfico del laboratorio
- [ ] Headers de seguridad y reducción de exposición aplicados
- [ ] Retest ejecutado
- [ ] Riesgos pendientes documentados para el Laboratorio 4
- [ ] Tag `lab-3` publicado

---

<div align="center">

**Secure Product Challenge · FDSI**
*Laboratorio 3 — Red Team + Blue Team · Uso académico autorizado*

</div>