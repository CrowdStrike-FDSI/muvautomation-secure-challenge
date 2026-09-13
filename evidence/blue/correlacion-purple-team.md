# 🔵 Fase D — Correlación de logs y detección (Purple Team)

**Fuente:** `evidence/blue/access.log`, `evidence/blue/error.log` (Nginx, host `fdsi` / `100.110.229.99`)
**Ventana analizada:** 10 sep 2026 (prueba local Fase A) y 13 sep 2026, 00:38–03:12 UTC (Fases B–D)

---

## 1. Línea de tiempo Purple Team

| Hora UTC | Acción Red Team | Evidencia Blue Team (`access.log` / `error.log`) | Conclusión |
|---|---|---|---|
| 00:38:59 | `curl -i $TARGET_URL/alertas` (Fase B, prueba de conectividad) | `100.80.65.73 GET /alertas 200 2 curl/8.20.0` | Correlación exacta con la captura de la Fase B (mismo segundo, mismo status). |
| 00:44:13 | `curl -i "$TARGET_URL/"` (Fase C, Paso 8, `curl_home.txt`) | `100.80.65.73 GET / 404 22 curl/8.20.0` | 404 registrado sin exponer información adicional. |
| 00:44:19 | `curl -I "$TARGET_URL/alertas"` (Fase C, `curl_headers.txt`) | `100.80.65.73 HEAD /alertas 405 0 curl/8.20.0` | Nginx reenvía el `405 Method Not Allowed` del backend tal cual. |
| 00:48:50–00:48:52 | `nmap -Pn -sT -sV -p 80` (fingerprinting con NSE) | **8 respuestas 404 en <3 s** desde la misma IP, 4 con `User-Agent: Nmap Scripting Engine` y rutas de sondeo típicas (`/HNAP1`, `/evox/about`, `/nmaplowercheck…`, `POST /sdk`) | **Dispara la regla de detección** (≥5×404 en 5 min) — el escaneo es identificable por ráfaga + firma de User-Agent, sin necesidad de payload. |
| 00:49:28 | `curl -i "$TARGET_URL/alertas"` (verificación post-escaneo) | `200 OK` | El servicio siguió disponible tras el escaneo de Nmap. |
| 01:10:17–01:12:18 | Exploración manual con ZAP + Firefox (`/docs`, `/openapi.json`, `/alertas`) | `GET /docs 200`, `GET /openapi.json 200` con `Referer: http://100.110.229.99/docs` | Confirma **R11**: Swagger UI carga automáticamente el esquema completo de la API sin autenticación ni intervención adicional del atacante. |
| 03:06:55–03:08:37 | *(sin comando Red Team — hallazgo no planeado)* | 4× `502 Bad Gateway` en `access.log` + 4× `connect() failed (111: Connection refused) ... upstream: http://127.0.0.1:8000` en `error.log` | El backend FastAPI se cayó/reinició durante la ventana de pruebas — **confirma en vivo R9** (persistencia solo en memoria; cualquier reinicio pierde las alertas). |
| 03:11:32–03:11:37 | `tcpdump` + `curl /alertas`, `/docs`, `/openapi.json` (Fase D, captura de tráfico) | 3× `200 OK`, mismos segundos exactos que los streams `tcp.stream eq 0,1,2` de `lab3-http-v2.pcap` | Correlación total entre log de aplicación y captura de red: mismo timestamp, mismo origen, mismo endpoint. |

**Total: 8 eventos correlacionados** (mínimo exigido: 3).

---

## 2. Regla de detección aplicada (Paso 13 de la guía)

```bash
awk '$9 == 404 {print $1, $4}' access.log
awk '$9 == 404 {print $1}' access.log | sort | uniq -c | sort -nr
grep -E 'Nmap|nmap' access.log
```

**Resultado:**

```
     12 100.80.65.73
      1 192.168.15.1
```

De esas 12, **8 ocurren entre las 00:44:13 y las 00:48:52** (una ventana de ~4.5 minutos) — cumple la regla del laboratorio: *"una misma IP produce cinco o más respuestas 404 en cinco minutos"*.

**Limitaciones de la regla (a documentar, per Paso 13):**
- Es una heurística basada en volumen, no en intención: un usuario legítimo con enlaces rotos también podría dispararla (falso positivo).
- No distingue un escaneo lento (1 request cada varios minutos) — un atacante paciente evade la ventana de 5 minutos (falso negativo).
- Depende de que el escáner no falsifique el `User-Agent`; la firma `Nmap Scripting Engine` es trivial de cambiar.
- Sin autenticación ni identidad (R7), la regla solo correlaciona por IP — en una red con NAT/proxy varias personas podrían compartir la misma IP de origen.

---

## 3. Repudiation (R7) — qué sí y qué no permite el log

**Sí permite:** con el `access.log` se pudo reconstruir, en 8 puntos independientes, exactamente qué comando de Red Team generó cada línea (mismo timestamp al segundo, mismo endpoint, mismo status code que las capturas de pantalla y el PCAP).

**No permite:** el log identifica una **IP de origen**, no una **identidad**. Nada en `access.log` prueba que fue *Robinson* o *Oscar* quien ejecutó el comando desde `100.80.65.73` — cualquiera con acceso a esa máquina (o a esa IP, si estuviera detrás de un NAT compartido) habría dejado el mismo rastro. Por eso **R7 permanece "Pendiente Lab 4"**: la trazabilidad real requiere autenticación e identidad, no solo telemetría de red.

---

## 4. Hallazgo adicional (no estaba en el alcance original)

Entre las 03:06:55 y las 03:08:37 UTC el backend devolvió `502 Bad Gateway` en 4 ocasiones (`error.log`: `connect() failed (111: Connection refused)` hacia `127.0.0.1:8000`). Esto ocurrió ~3 minutos antes de la captura de tráfico exitosa (03:11:32). Es evidencia en vivo de **R9** (alertas solo en memoria — un reinicio del proceso `uvicorn` las pierde) y conviene dejarlo anotado en el registro de riesgos como observación reforzada, no como un riesgo nuevo.

---

## 5. Nota sobre `journalctl`

```bash
sudo journalctl -u nginx --since '2026-09-13 02:50:00' --until '2026-09-13 03:20:00' --no-pager
# -- No entries --
```

`journalctl` no devolvió nada para esa ventana porque Nginx escribe su telemetría de acceso/error a los archivos de `/var/log/nginx/` (configuración por defecto), no a `stdout`/`journald`. El `unit journal` de systemd solo captura eventos del propio proceso (arranque, recarga, fallos de servicio), no las peticiones HTTP — por eso la Fase D depende de `access.log`/`error.log` y no de `journalctl` para la correlación.
