# 0006. Medición de energía con IC dedicado para llegar a clase 1

- Status: proposed
- Date: 2026-11-15
- Deciders: JB, Gabriel
- Requirements: REQ011, REQ014

## Contexto y problema

Hoy la medición es analógica: ZMPT101L (tensión) + ZMCT102 (corriente) al ADC del ESP32, calibrada
a 2-3 %. Para facturar por kWh el objetivo es clase 1 (±1 %). El ADC del ESP32 es no lineal y
sensible a temperatura; llegar a 1 % con él es posible pero costoso en calibración por unidad.

## Opciones consideradas

1. Mantener analógico y calibrar cada unidad en la línea (fixture + patrón)
2. IC de medición monofásico con interfaz digital (ATM90E26, BL0940, HLW8032, CSE7766) y shunt o CT
3. Módulo de medición certificado externo (más caro, más grande)

## Decisión

Pendiente. Propuesta: **opción 2** con un IC que ya tenga historial en medidores clase 1 (ATM90E26 o
BL0940), manteniendo el CT para aislación. Se valida en bench contra un patrón clase 0.5 antes de
aceptar.

## Consecuencias

- Libera el ADC del ESP32 y el TR1 (ZMPT101L, el componente más caro localmente: USD 13.5).
- Requiere rediseño del bloque de medición en rev B y firmware nuevo para el IC (SPI/UART).
