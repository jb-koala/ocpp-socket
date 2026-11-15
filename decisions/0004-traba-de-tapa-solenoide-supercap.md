# 0004. Reemplazar el servo de la tapa por solenoide + supercapacitor

- Status: proposed
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ006

## Contexto y problema

Hoy la tapa se traba con un servo. Si el socket pierde alimentación con la tapa trabada, el
usuario no puede retirar el cable.

## Opciones consideradas

1. Mantener el servo y agregar llave mecánica de emergencia
2. Solenoide normalmente abierto (traba solo con energía) — se libera solo al perder energía
3. Solenoide bi-estable + supercapacitor que dispara la liberación al detectar caída de tensión

## Decisión

Pendiente. Se inclina por la **opción 3** (menor consumo en reposo que la 2, que mantendría el
solenoide energizado toda la sesión y afecta `idle_power`). Hay que medir el consumo real en bench
antes de aceptar.

## Consecuencias

- Qué hay que cambiar en el repo si se acepta: circuito de detección de caída + driver en `hw/`,
  entrada `lock_release` en `session_guard`, actualización de `bom/` (supercap, solenoide).
