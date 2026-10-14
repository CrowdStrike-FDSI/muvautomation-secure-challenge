## Baseline

| Binario | Formato | Arquitectura | Tipo | Linking | Símbolos |
|---|---|---|---|---|---|
| crackme_level1 | ELF64 LSB | x86-64 | EXEC (entry 0x401070) | dinámico (ld-linux-x86-64.so.2, libc.so.6) | sí (not stripped, debug_info) |
| crackme_level2 | ELF64 LSB | x86-64 | EXEC (entry 0x401070) | dinámico | sí (not stripped, debug_info) |
| crackme_level2_stripped | ELF64 LSB | x86-64 | EXEC | dinámico | no (stripped) |

Al ser EXEC y no PIE, las direcciones son fijas entre ejecuciones.
Evidencia: baseline.txt y screenshots/01 y 02.

### ¿Por qué sirve un hash?

SHA-256 genera una huella de tamaño fijo a partir del contenido del archivo.
Si cambia un solo byte, el hash cambia por completo (lo comprobé modificando
un byte en una copia). Comparar el hash calculado con el oficial garantiza que
todos los equipos analizan exactamente el mismo binario, sin corrupción en la
descarga ni modificaciones, y que mi análisis es reproducible por otros.
