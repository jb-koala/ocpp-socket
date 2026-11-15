# 0002. Implementar OCPP 1.6-J antes que 2.0.1

- Status: accepted
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ001

## Contexto y problema

Los CSMS con los que opera Fluxio hoy hablan 1.6-J. OCPP 2.0.1 es más completo pero más pesado
y todavía poco desplegado en el mercado local.

## Opciones consideradas

1. OCPP 1.6-J
2. OCPP 2.0.1
3. Ambos desde el inicio

## Decisión

**1.6-J** ahora. El código de transporte (WebSocket, cola de mensajes, reintentos) se escribe de
forma que 2.0.1 sea otro módulo de mensajes, no una reescritura.

## Consecuencias

- Buenas: compatibilidad inmediata con los backends existentes; menos RAM.
- Malas: 2.0.1 queda como deuda; algunas funciones (ISO 15118, smart charging avanzado) no están.
