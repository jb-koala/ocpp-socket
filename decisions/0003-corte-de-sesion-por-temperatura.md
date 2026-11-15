# 0003. El MCU corta la sesión por temperatura sin esperar al CSMS

- Status: accepted
- Date: 2026-11-15
- Deciders: JB
- Requirements: REQ003, REQ004

## Contexto y problema

Un socket con relé y bornes de 16 A en un gabinete cerrado puede calentarse por mal contacto o
ambiente. Reportar la temperatura al CSMS no alcanza: la latencia de red o una desconexión no
pueden dejar la carga activa.

## Opciones consideradas

1. Solo reportar temperatura; que el CSMS decida (`RemoteStopTransaction`)
2. El MCU corta localmente y notifica (`StopTransaction` con reason `Other` + `StatusNotification` Faulted)
3. Termostato bimetálico en serie con el relé, sin lógica

## Decisión

**Opción 2**, con umbrales en `reqs/budgets.yml` (`safety.*`) y lógica en
`firmware/lib/session_guard` testeable en laptop. Se evalúa sumar la opción 3 como respaldo
físico en rev B.

## Consecuencias

- Buenas: la protección no depende de la red. Los umbrales están en un solo lugar y tienen tests.
- Malas: hay que calibrar el sensor contra la temperatura real de los bornes en bench.
