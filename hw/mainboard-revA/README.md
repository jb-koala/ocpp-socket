# mainboard rev A

Estado: **sin esquemático todavía**. Arquitectura en `docs/architecture.c4`, bloques:

| Bloque | Parte (ver bom/) | Notas |
|---|---|---|
| MCU | ESP32-S3-WROOM-1 | USB nativo a conector para flash/logs; UART0 a header de debug |
| Fuente | módulo AC/DC 5 V + LDO 3.3 V | fusible y varistor en entrada |
| Potencia | relé 16 A + driver | el botón de emergencia (SW1) va en serie con el contacto, no pasa por el MCU |
| Medición | medidor de energía | aislado del MCU (optoacoplador o aislador digital) |
| Temperatura | NTC sobre bornes | divisor a ADC; **el umbral está en reqs/budgets.yml**, no en hardware |
| Traba | servo (rev A) / solenoide (ver decisions/0004) | |
| Expansión | 2x8 header: 3V3, 5V, GND, SPI, I2C, UART1, 2 GPIO | pinout a definir en `pinout.md` |

Para crear el proyecto: KiCad 10 → New Project → `mainboard-revA.kicad_pro` en esta carpeta.
