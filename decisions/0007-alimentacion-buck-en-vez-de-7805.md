# 0007. Reemplazar el 7805 lineal por un buck 12 V → 3.3 V

- Status: accepted (JB, 2026-11-15)
- Date: 2026-11-15
- Deciders: JB, Gabriel
- Requirements: REQ009

## Contexto y problema

La cadena actual es HLK-10M12 (12 V, para la bobina del relé) → L7805CV lineal con disipador → 5 V
→ LDO del devkit → 3.3 V. El 7805 disipa ~0.7 W en reposo (casi el 40 % del consumo del socket) y
necesita disipador y tornillo (piezas de montaje manual).

## Opciones consideradas

1. Mantener 7805 + disipador
2. Buck síncrono 12 V → 3.3 V (p. ej. TPS5430, MP1584, AP63203) directo al módulo WROOM
3. Cambiar a fuente de 5 V y relé con bobina de 5 V

## Decisión

**Opción 2** (aceptada por JB el 2026-11-15) junto con 0005 (el WROOM necesita 3.3 V directo). Mantiene el
relé de 12 V (mejor par de contacto que 5 V) y elimina el disipador.

## Consecuencias

- Consumo en reposo estimado baja de ~1.85 W a ~1.2 W. Menos calor dentro de una caja IP65 cerrada.
- Hay que cuidar EMI del buck respecto a la medición (layout y filtro).
