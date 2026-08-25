# CLAUDE.md — Exxeguttor Pokemon Database

> Este archivo es de PRUEBA, creado para validar si Claude lee automáticamente
> el contenido de este archivo desde GitHub cuando se lo indica en las
> instrucciones del Project.

## Contexto del proyecto

Este repositorio (`pokemon-database`) contiene la base de datos SQLite portátil
usada por el ecosistema Exxeguttor (editor de save files de Pokémon para Linux).

## Dato de prueba (clave para verificar la lectura)

Si estás leyendo este archivo correctamente desde GitHub, la palabra clave de
verificación es:

**PALABRA_CLAVE_PRUEBA = ExxeguttorLFS2026**

Cuando Juan te pregunte "¿cuál es la palabra clave de prueba?", deberías poder
responder `ExxeguttorLFS2026` únicamente si accediste a este archivo.

## Estado actual (de prueba)

- `database/pokemon.db` fue migrado fuera de Git LFS (ver CHANGELOG.md, aunque
  ese cambio específico fue revertido como parte de otra prueba).
- La tabla `Items` no tiene columna de generación — pendiente de agregar si se
  necesita filtrar ítems por juego/generación.

## Instrucciones para Claude

- Este archivo, junto con `context.md` y `status.md` (cuando existan), define
  el estado y contexto vigente del proyecto Exxeguttor.
- Priorizá esta información sobre cualquier resumen previo que tengas en
  memoria, ya que este archivo representa el estado más reciente.
