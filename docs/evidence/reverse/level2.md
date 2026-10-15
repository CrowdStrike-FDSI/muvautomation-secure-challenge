# Nivel 2 — Ghidra: reconstruir la validación

## Observación inicial
- El binario conserva símbolos (`not stripped`, `debug_info`): `nm` lista `main`,
  `validate_key` y `reveal_flag`.
- `strings` muestra `Uso: %s <license-key>`, `License accepted.` e `Invalid license.`

## Casilla 1: función de validación desde `main`
- `main` en `0x401267`; `validate_key` en `0x401156`; `reveal_flag` en `0x4011f3`.
- Decompilado de Ghidra: `if (argc == 2) { iVar1 = validate_key(argv[1]); ... }`
- Si `validate_key` devuelve 0: `Invalid license.` y retorno 3.
  Si devuelve distinto de 0: `License accepted.`, `reveal_flag()` y retorno 0.
- En ensamblador (objdump):
  - `4012cd`: `call validate_key` (con `argv[1]` en `rdi`)
  - `4012d2`: `test eax,eax`
  - `4012d4`: `je 4012f1`, salta a la rama de error si eax == 0
  - `4012e5`: `call reveal_flag`, solo se alcanza si la validación pasó
## Casilla 2: longitud esperada de la clave
- Decompilado de `validate_key`: `strlen(candidate) == 0x11`, es decir, **17 caracteres**.
- El bucle `for (i = 0; i < 0x11; i++)` recorre exactamente 17 posiciones.
- Contraste: el símbolo `expected.0` (`.rodata`, `0x402090`) mide 0x11 = 17 bytes
  (`nm -S crackme_level2 | grep expected`).
- Si la longitud no es 17, la función devuelve 0 sin comparar nada
  (`Invalid license.`).
## Casilla 3: transformación aplicada a cada byte
- Operador: **XOR** byte a byte.
- Cuerpo del bucle (ensamblador de `validate_key`):
  - `4011a8: and eax,0x3` → índice cíclico `i & 3` (equivale a `i % 4`).
  - `4011ae: lea rax,[rip+0xed6]  # 40208b <k.1>` → arreglo pequeño `k.1`, 4 bytes.
  - `4011b9: xor eax,ecx` → `transformed = k[i & 3] ^ candidate[i]`.
  - `4011be: lea rdx,[rip+0xecb]  # 402090 <expected.0>` → arreglo esperado, 17 bytes.
  - `4011cf: xor al,[rbp-0x19]` → `expected[i] ^ transformed`.
  - `4011d5: or [rbp-0x4],eax` → acumula en `score`.
- Datos (`objdump -s`):
  - `expected` @ 0x402090 (17 bytes): `65 15 44 23 0e 03 52 3c 66 03 44 2f 0e 63 27 58 15`
  - `k.1` @ 0x40208b (4 bytes): `23 51 17 6a`
- La licencia es válida solo si `score == 0`, es decir, si para las 17 posiciones
  `candidate[i] ^ k[i & 3] == expected[i]`.
- Como XOR es reversible, la inversa es `candidate[i] = expected[i] ^ k[i & 3]`.
## Casilla 4: clave reconstruida y FLAG
- Script: `docs/evidence/reverse/solver_level2.py`
  (aplica `candidate[i] = expected[i] ^ k[i & 3]` sobre los 17 bytes).
- Autoverificación en Python: `score == 0` (válida).
- Clave reconstruida: `FDSI-REVERSE-2026`
  (bytes `46 44 53 49 2d 52 45 56 45 52 53 45 2d 32 30 32 36`).
- Prueba negativa: `./crackme_level2 AAAAAAAAAAAAAAAAA` → Invalid license.
  (17 caracteres: pasa el filtro de longitud y falla en el bucle XOR).
- Prueba negativa de longitud: `FDSI-REVERSE-202` (16) y `FDSI-REVERSE-20266` (18)
  → Invalid license. El filtro de longitud actúa antes del bucle.
- Prueba positiva: `./crackme_level2 'FDSI-REVERSE-2026'`
  → License accepted.
  → FLAG: `FLAG{ghidra_plus_gdb}`

## Reflexión de desarrollo seguro
La clave se dedujo solo con análisis estático: dos arreglos constantes en `.rodata`
y un XOR reversible. Una validación basada en una operación reversible con datos
embebidos no protege el secreto, porque cualquiera con el binario puede invertirla.
Además, los símbolos y la información de depuración (`validate_key`, `reveal_flag`,
`expected`, `score`) y la ruta del fuente facilitaron la lectura.
## Casilla 5: decompilado anotado en Ghidra
Renombres aplicados en `validate_key`:

| Original | Renombrado | Significado |
|---|---|---|
| `candidate` | `input_key` | clave introducida por el usuario |
| `sVar2` | `input_len` | resultado de `strlen` (debe ser 0x11 = 17) |
| `uVar1` | `result` | valor de retorno (1 = válida, 0 = inválida) |
| `transformed` | `xored` | valor intermedio generado por el compilador |
| `score` | `diff_acc` | acumulador de diferencias (0 = todo coincide) |
| `i` | `idx` | índice del bucle (0..16) |

Comentarios añadidos:
- Sobre `if (input_len == 0x11)`: la clave debe medir exactamente 17 caracteres.
- Sobre el bucle: `expected[idx] ^ k[idx & 3] ^ input_key[idx]` debe ser 0 en cada byte.

Nota: en el listado de ensamblador Ghidra reutiliza el nombre `result` para el registro
EAX/RAX porque comparte almacenamiento con esa variable; es solo cosmético.

Captura: `screenshots/08-level2-ghidra-anotado.png`
## Boss Level — binario sin símbolos (crackme_level2_stripped)

### Qué información desapareció al hacer strip
- `file`: pasó de "with debug_info, not stripped" a "stripped".
- `nm`: ya no lista `validate_key`, `main` ni `expected.0` ("no symbols").
- `readelf -S`: ya no existen `.symtab` ni las secciones `.debug_*`.
- Se perdieron nombres de funciones y variables (`validate_key`, `k.1`, `expected.0`), líneas de código y la ruta del `.c`.
- Se conservan: el código, `.rodata`, las cadenas, los símbolos dinámicos de libc (`strlen`, `puts`, `printf`, `putchar`).
- Tamaño: 18200 bytes (con símbolos) frente a 14424 bytes (stripped).

### Cómo recuperé la lógica de validación
1. `strings`: siguen apareciendo `License accepted.`, `Invalid license.` y `Uso: %s <license-key>`.
2. En `_start`, `mov rdi,0x401267` justo antes de `call __libc_start_main` indica que `main` está en `0x401267`.
3. En `main`: con argc == 2 prepara `argv[1]`, ejecuta `call 0x401156`, luego `test eax,eax; je 4012f1`. Si es 0 imprime "Invalid license." y sale con 3; si no, imprime "License accepted." y llama a `0x4011f3` (rutina que imprime la FLAG con XOR 0x37).
4. La función `0x401156` es la validación: compara `strlen` con 0x11 (17), recorre los bytes, aplica XOR con una tabla de 4 bytes en `0x40208b` (índice `i & 3`) y compara con el arreglo esperado en `0x402090`. Acumula las diferencias con OR y devuelve `diff == 0`.
5. Comparé el desensamblado de `0x401156` en ambos binarios: las instrucciones son idénticas; solo desaparecen las etiquetas (`validate_key`, `k.1`, `expected.0`).

### Pseudocódigo recuperado

    int validar(char *clave) {
        if (strlen(clave) != 17) return 0;
        int diff = 0;
        for (size_t i = 0; i < 17; i++) {
            unsigned char t = clave[i] ^ tabla[i & 3];
            diff |= esperado[i] ^ t;
        }
        return diff == 0;
    }

### Prueba
`./crackme_level2_stripped FDSI-REVERSE-2026` -> `License accepted.` y `FLAG{ghidra_plus_gdb}`.

### Conclusión
Quitar símbolos no oculta la lógica: dificulta la lectura, pero las referencias a cadenas, las llamadas a libc y el flujo de control permiten reconstruirla.
