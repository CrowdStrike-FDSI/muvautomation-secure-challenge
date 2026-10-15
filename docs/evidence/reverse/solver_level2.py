#!/usr/bin/env python3
"""Reconstruye la clave de crackme_level2 a partir de los datos de .rodata."""

# Datos extraídos con: objdump -s -j .rodata crackme_level2
expected = bytes.fromhex("65154423 0e03523c 6603442f 0e632758 15".replace(" ", ""))
k        = bytes.fromhex("2351176a")          # arreglo pequeño k.1 (4 bytes)

assert len(expected) == 17, "expected debe medir 17 bytes"
assert len(k) == 4, "k debe medir 4 bytes"

# Inversa de la validación: candidate[i] = expected[i] ^ k[i & 3]
candidate = bytes(expected[i] ^ k[i & 3] for i in range(len(expected)))

print("bytes :", candidate.hex(" "))
print("texto :", candidate.decode("ascii", errors="replace"))

# Autoverificación: simula validate_key tal como la leíste en el ensamblador
score = 0
for i in range(len(candidate)):
    transformed = candidate[i] ^ k[i & 3]
    score |= expected[i] ^ transformed
print("score :", score, "->", "VÁLIDA" if score == 0 else "INVÁLIDA")
