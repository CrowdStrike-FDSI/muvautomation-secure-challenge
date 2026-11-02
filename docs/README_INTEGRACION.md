# Integración al repositorio

## Estado de la fase 1 (análisis estático)

| Paso | Estado |
|---|---|
| Línea base y alcance | Hecho: commit `bbbb4cd3f71246882c0b9fde074059480b7e9b7f` en `main` |
| SAST con Semgrep en Actions | Hecho: 10 hallazgos (`resultado-semgrep`) |
| Detección de secretos con Gitleaks | Hecho con `GITLEAKS_LICENSE` (ver nota 3) |
| SCA | Pendiente: crear `requirements.txt` y ejecutar `pip-audit` / revisar Dependabot |
| Controles nativos de GitHub (CodeQL, Dependabot, secret scanning) | [Confirmar cuáles se activaron] |
| Triage, foto actual y plan de remediación | Hecho: `docs/SECURITY.md` y `docs/REPORTE_HALLAZGOS.md` |
| DAST pasivo y pentest | Fase 2 |

Este análisis es **solo estático**: no se despliega la aplicación, no se ejecutan pruebas y no se instalan las dependencias del proyecto. No se usó el workflow `dast-staging.yml`, que requiere la variable `STAGING_URL`.

## Pasos de la integración

1. Copie `.github/workflows/seguridad-estatica.yml` y la carpeta `docs/` a la raíz del proyecto, respetando las rutas.
2. En GitHub vaya a **Settings → Security / Advanced Security** y habilite lo disponible: CodeQL **Default setup**, Dependabot alerts y secret scanning. La disponibilidad varía según visibilidad y plan; no añada un segundo workflow CodeQL si usa Default setup.
3. Haga un commit en una rama `security/lab-fsi`, abra un Pull Request y revise **Actions**. Descargue `resultado-semgrep`. Si Gitleaks requiere licencia por estar en una organización, documente la limitación y use la alternativa GitHub secret scanning o CLI.
4. Revise la pestaña **Security**, si su repositorio tiene acceso a las funcionalidades. No asuma que las alertas siempre estarán disponibles.
5. Solo si controla un staging HTTPS (fase 2): configure la variable de repositorio `STAGING_URL`, compruebe permisos y ejecute manualmente **Actions → DAST pasivo - staging autorizado → Run workflow**. El pipeline **no verifica la titularidad del dominio**: es su responsabilidad autorizarlo. No configure endpoints de terceros o producción.
6. Descargue `informe-zap` y registre los resultados en `docs/SECURITY.md`.
7. Cree al menos un Pull Request de remediación y vuelva a ejecutar el análisis; documente antes y después.
8. Agregue en el `README.md` un enlace relativo a `[Informe de seguridad](docs/SECURITY.md)` y el estado del pipeline (opcional: badge de workflow).

## Cómo obtener el resumen del escaneo estático

Descargue el artefacto `resultado-semgrep` (página **Summary** de la ejecución, sección **Artifacts**) y, dentro de su carpeta, ejecute:

```
py -c "import json; d=json.load(open('semgrep.json')); print(len(d['results']),'hallazgos'); [print(r['extra']['severity'], r['path'], r['start']['line'], r['check_id']) for r in d['results']]"
```

SCA local sin instalar las dependencias del proyecto (con `requirements.txt` ya creado y versiones fijadas con `==`):

```
py -m pip install --user pip-audit
py -m pip_audit -r requirements.txt --no-deps --disable-pip -f json -o sca.json
```

## Notas

1. `|| true` en el trabajo de Semgrep y el baseline ZAP impide bloquear el primer laboratorio; el estado verde NO significa aplicación segura. Adapte reglas y cambie a un control estricto cuando haya triage.
2. No suba reportes con datos sensibles a repositorios públicos.
3. **Gitleaks:** la acción `gitleaks/gitleaks-action` exige licencia en repositorios de organizaciones (`GITLEAKS_LICENSE` como secreto del repositorio). Sin ella, el job falla con `missing gitleaks license`. Alternativa sin licencia: ejecutar el CLI de Gitleaks en el workflow.
4. Un comentario en el workflow (línea que empieza con `#`) no tiene ningún efecto; lo que habilita la licencia es la variable `GITLEAKS_LICENSE` en la sección `env` del paso.
5. **Acciones sin fijar:** Semgrep marca como hallazgo (F-03) las acciones por etiqueta (`@v3`, `@v4`, `@v5`). Para la remediación, fije cada `uses:` a un SHA de commit de 40 caracteres.