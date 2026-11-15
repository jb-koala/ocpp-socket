# Glosario

| Término | Significado |
|---|---|
| OCPP | Open Charge Point Protocol. El socket implementa 1.6-J (JSON sobre WebSocket). |
| CSMS | Charging Station Management System: el backend con el que habla el socket. |
| Sesión / transacción | Período entre `StartTransaction` y `StopTransaction` en OCPP 1.6. |
| MeterValues | Mensaje OCPP periódico con energía, potencia, temperatura, etc. |
| Corte por temperatura | El MCU interrumpe la sesión si el sensor del bloque de potencia supera el umbral (REQ004). |
| OTA | Actualización de firmware remota. En OCPP 1.6: `UpdateFirmware`. |
| Puerto de expansión | Conector para módulos: SD (RFID offline + logs), LoRa, segundo MCU. |
| Bench | Banco de pruebas con la placa real, sin vehículo, con carga resistiva. |
| Rev A | Primera revisión de la mainboard en KiCad. |
