# Informe técnico de hallazgos

**Proyecto:** MuvAutomation Secure Challenge — Falcon Incident Hub (API de alertas con FastAPI y Nginx)  
**Integrantes:** Oscar Andrés Sánchez Porras, Robinson Steven Núñez Portela [verificar la lista antes de entregar]  
**Repositorio / commit:** https://github.com/CrowdStrike-FDSI/muvautomation-secure-challenge / `bbbb4cd3f71246882c0b9fde074059480b7e9b7f`  
**Entorno autorizado:** solo el repositorio (análisis estático, sin ejecutar el código). [Responsable y fecha de autorización]  
**Fecha:** 28 de octubre de 2026

## Resumen ejecutivo
El análisis estático (fase 1) encontró 9 hallazgos distintos: 1 crítico, 1 alto, 4 medios y 3 bajos. Los tres riesgos principales son:

1. **F-01 (crítico):** la clave que firma los JWT está escrita en `app/main.py` y publicada en un repositorio público. Quien la lea puede fabricar tokens con rol `analyst` y escribir alertas o leer la auditoría.
2. **F-02 (alto):** las contraseñas de los usuarios demo están en el código y en comentarios del repositorio público.
3. **F-03 (medio):** los workflows de GitHub Actions usan acciones por etiqueta mutable (6 ocurrencias), lo que abre la puerta a un ataque a la cadena de suministro.

Aún no se ha corregido nada: el estado es la foto actual. El plan es corregir F-01 y F-02 (100 % de los críticos y altos, por encima del mínimo del 50 %) y, si hay tiempo, F-03 y F-04. La foto futura se genera al reejecutar el escaneo tras fusionar el Pull Request.

## Metodología
Identificación del alcance → SAST (Semgrep, con revisión manual de `app/main.py` y `nginx/muvautomation.conf`) → detección de secretos (Gitleaks y búsqueda en el historial de 26 commits) → SCA (pendiente de `requirements.txt`) → DAST pasivo (fase 2) → validación manual no destructiva (fase 2) → corrección → reescaneo.

Severidad unificada: ERROR de Semgrep → High; WARNING → Medium; INFO → Low; secretos que permiten falsificar identidad → Critical.

## Hallazgo F-01
- **Título:** Clave de firma de JWT escrita en el código fuente.
- **Categoría OWASP/CWE (si corresponde):** OWASP A07 (fallas de identificación y autenticación); CWE-798 y CWE-522.
- **Severidad y justificación:** Crítica. El repositorio es público y la misma clave se usa para validar los tokens del servicio desplegado. Quien la conozca puede crear un token válido con rol `analyst` sin credenciales.
- **Evidencia minimizada, sin credenciales ni datos personales:** regla `python.jwt.security.jwt-hardcode.jwt-python-hardcoded-secret` en `app/main.py`, línea 124, del artefacto `semgrep.json`. Bandit lo marca como `B105` en la línea 30. El valor de la clave no se reproduce en este informe.

  **Captura del estado ANTES (F-01):** detalle del hallazgo `jwt-python-hardcoded-secret` en `app/main.py`, línea 124 (no muestra el valor de la clave).

  ![Antes: F-01](../evidence/lab5/antes/antes-02b-semgrep-detalle-hallazgos.png)
- **Impacto en confidencialidad, integridad o disponibilidad:** Confidencialidad: lectura de `/alertas` y `/audit`. Integridad: creación y modificación de alertas, y atribución falsa en el log de auditoría. Disponibilidad: bajo.
- **Pasos de validación segura en entorno propio:** [pendiente, fase 2] Firmar un token de prueba con la clave en el entorno propio y comprobar que el servicio lo acepta; después rotar la clave y comprobar que ese token recibe `401`.
- **Corrección (commit / pull request):** [pendiente] Leer `SECRET_KEY` desde la variable de entorno (la app falla al arrancar si no existe), generar una clave nueva y configurarla en systemd fuera del repositorio.
- **Resultado del reescaneo:** [pendiente] Esperado: la regla `jwt-python-hardcoded-secret` ya no aparece.

## Hallazgo F-02
- **Título:** Contraseñas de usuarios demo visibles en el repositorio.
- **Categoría OWASP/CWE (si corresponde):** OWASP A07; CWE-798.
- **Severidad y justificación:** Alta. Las contraseñas están en el código y en comentarios de un repositorio público; sirven para obtener un token legítimo si no se han cambiado en el servidor. Semgrep no lo detectó, se identificó por revisión manual.
- **Evidencia minimizada, sin credenciales ni datos personales:** bloque `fake_users_db` de `app/main.py`. Las contraseñas no se reproducen aquí.

  **Captura del estado ANTES (F-02):** no hay captura propia, porque Semgrep no detectó este hallazgo (se identificó por revisión manual). Las contraseñas no se muestran. El resultado general del escaneo está en:

  ![Antes: resultado de Semgrep](../evidence/lab5/antes/antes-02-semgrep-10-hallazgos.png)
- **Impacto en confidencialidad, integridad o disponibilidad:** Confidencialidad e integridad, según el rol de la cuenta (`analyst` escribe, `viewer` lee).
- **Pasos de validación segura en entorno propio:** [pendiente, fase 2] Iniciar sesión en el entorno propio con una cuenta de laboratorio y comprobar que, tras el cambio, las contraseñas del repositorio ya no funcionan.
- **Corrección (commit / pull request):** [pendiente] Cargar usuarios y hashes desde variables de entorno, eliminar las contraseñas del código y comentarios, y cambiar las contraseñas actuales.
- **Resultado del reescaneo:** [pendiente]

## Hallazgo F-03 (resumen)
- **Título:** Acciones de GitHub fijadas por etiqueta mutable.
- **Categoría OWASP/CWE (si corresponde):** OWASP A08; CWE-1357 y CWE-353.
- **Severidad y justificación:** Media. Si el autor de una acción reapunta la etiqueta, el pipeline ejecutaría código no revisado. Se detectaron 6 ocurrencias en `seguridad-estatica.yml` y `dast-staging.yml`.
- **Corrección (commit / pull request):** [pendiente] Fijar cada `uses:` a un SHA de 40 caracteres.

## Otros hallazgos registrados
F-04 (Nginx usa `$host`, CWE-290, 3 ocurrencias), F-05 (sin `requirements.txt`, no hay SCA), F-06 (sin límite de intentos en `/token`), F-07 (`status` sin validar), F-08 (Swagger habilitado en la app) y F-09 (evidencia con hostnames e IPs en repositorio público). El detalle está en `docs/SECURITY.md`, sección 3.

## Reflexión final
Semgrep detectó la clave escrita en el código, las acciones sin fijar y el uso de `$host`; no detectó las contraseñas demo, la falta de límite de intentos ni la validación de entrada, que salieron de la revisión manual. Gitleaks y el historial no mostraron claves privadas ni tokens reales, pero eso no cubre una clave en forma de texto simple como `SECRET_KEY`. El SCA no se pudo completar porque el proyecto no tenía archivo de dependencias, lo que es en sí mismo un hallazgo. Un estado verde en el pipeline no significa aplicación segura, porque los pasos usan `|| true`. Para integrar seguridad en el ciclo de desarrollo: gestionar secretos fuera del repositorio desde el primer commit, fijar dependencias y acciones, y pasar el escaneo estático en cada Pull Request con triage de resultados.