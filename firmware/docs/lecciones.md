# Lecciones Aprendidas - OCPP Socket Charger
*Se actualiza después de cada corrección del usuario.*

---

## Reglas de este Proyecto

- **Plataforma:** ESP32-S3 con Arduino framework
- **Librería OCPP:** MicroOcpp — no mezclar con otras
- **Persistencia:** `Preferences` (NVS) — NO usar EEPROM deprecated
- **No bloquear el loop:** `millis()` para timers, NUNCA `delay()` en loop()
- **Modularidad:** El `.ino` orquesta; módulos en `.h`/`.cpp` separados
- **El .ino debe llamarse igual que la carpeta** → `occp-socket-charger.ino`

---

## Lecciones Capturadas

### L-001: El IdTag es crítico para que el servidor acepte la transacción
**Contexto:** La versión v2.0 usaba `"B0703B"` como idTag y las transacciones fallaban silenciosamente.  
**Causa:** El servidor OCPP valida el idTag contra su base de datos. Un idTag no registrado devuelve `Rejected` sin error visible en el firmware.  
**Regla:** Siempre verificar el idTag contra el servidor antes de asumir que la lógica de botón falla. El idTag funcional es `"045740224D6080"`.

### L-002: La lógica de debounce compleja falla con sensores táctiles
**Contexto:** La versión v2.0 usaba un sistema de debounce con `stableButtonState` + `lastTimeLow` + 300ms que nunca disparaba el press corto.  
**Causa:** El sensor táctil oscila brevemente entre HIGH y LOW. Con debounce de "release", si el sensor baja aunque sea 1ms, el timer se resetea y `duration < 50ms` → no se ejecuta la acción.  
**Regla:** Para sensores táctiles usar debounce simple: `digitalRead == HIGH && millis() - ultimoBotonazoAt > 800ms`. Ejecutar la acción en el flanco de bajada (release).

### L-003: Nunca usar `cat` para monitorear serial en macOS
**Contexto:** `stty -f /dev/cu.usbmodem... 115200 && cat /dev/...` muestra caracteres basura.  
**Causa:** `cat` no configura el terminal en modo raw correctamente para USB CDC.  
**Regla:** Usar siempre `screen /dev/cu.usbmodem... 115200` o `arduino-cli monitor`. Los primeros ~3 segundos tienen basura del bootloader del ESP32-S3 — es normal.

### L-004: Cerrar el monitor serial antes de flashear
**Contexto:** `arduino-cli upload` falla con `[Errno 16] Resource busy` si `screen` u otro proceso tiene el puerto abierto.  
**Regla:** Antes de flashear, verificar con `lsof /dev/cu.usbmodem...` y cerrar `screen` con `Ctrl+A K`.

### L-005: La arquitectura modular compleja puede romper lo que funciona
**Contexto:** La versión v2.0 con `LedController`, `RelayController`, `WiFiProvisioning` todos integrados al mismo tiempo dejó de funcionar el touch/OCPP.  
**Regla:** Partir de la versión mínima que funciona y agregar módulos de a uno, verificando en hardware después de cada cambio. No hacer big-bang refactors.

### L-007: `huge_app` no soporta OTA — usar `default_8MB`
**Contexto:** ArduinoOTA autenticaba correctamente pero devolvía "No response from device". Ping al ESP32 mostraba 140ms de latencia (normal < 5ms), sugiriendo bloqueo de `mocpp_loop()`.  
**Causa real:** `huge_app` solo tiene UNA partición de app (`ota_0`). OTA en ESP32 necesita DOS (`ota_0` + `ota_1`). Al llamar `Update.begin()`, falla silenciosamente porque no hay segunda partición y el ESP32 nunca responde al host.  
**Regla:** Para cualquier proyecto ESP32 que necesite OTA, usar `PartitionScheme=default_8MB` desde el primer flash. La partición `default_8MB` tiene app0 + app1 de 3.25MB cada una, suficiente para firmware de hasta ~3MB.  
**Costo:** Requiere UN flash por USB para migrar. Después de ese flash, todo el futuro se hace por WiFi con el servidor HTTP OTA en puerto 8266.

### L-006: El relay debe estar en estado seguro (LOW) por defecto
**Regla:** `pinMode(PIN_RELAY, OUTPUT); digitalWrite(PIN_RELAY, LOW)` siempre en `setup()`. El relay solo debe ser HIGH cuando la transacción está activa y confirmada por el servidor.

### L-007: ESP32-S3 en este proyecto tiene 4MB de flash (NO 8MB)
**Contexto:** "Embedded PSRAM 8MB" en la salida de esptool se refiere a la PSRAM (RAM), NO al flash. El flash es de 4MB.  
**Error:** `PartitionScheme=default_8MB` requiere 8MB de flash → bootloop con: `partition 3 invalid - offset 0x340000 exceeds flash chip size 0x400000`.  
**Solución:** Usar `PartitionScheme=min_spiffs` para OTA con 4MB flash: 1.9MB por partición app, suficiente para firmware de 1.43MB.  
**Regla:** En este proyecto, SIEMPRE compilar y subir con `PartitionScheme=min_spiffs`.

### L-008: Dos instancias de WebServer como globales causan crash en ESP32 Arduino core 3.3.7
**Contexto:** `WiFiProvisioning` ya tiene un `WebServer _server(80)` como miembro. Agregar `WebServer otaServer(8266)` como global también causa crash antes de `setup()`.  
**Error:** Firmware crasha silenciosamente (solo `rst:0x3`) sin ningún output serial.  
**Solución:** Declarar el segundo WebServer como puntero global (`WebServer *otaServer = nullptr`) e inicializarlo con `new WebServer(8266)` solo cuando se necesita (en `setupOtaServer()`).

### L-009: Formato de URL de OCPP requiere el ID concatenado
**Contexto:** El servidor rechazaba la conexión WebSocket iniciada por `MicroOcpp` arrojando un error y quedando offline.
**Causa real:** El protocolo OCPP espera que la conexión se inicie hacia un endpoint que termine con el ID del punto de carga (ej: `ws://ip:puerto/ws/ID_DEL_CARGADOR`).
**Solución/Regla:** El firmware debe armar dinámicamente la URL completa anexando el ID al final antes de llamar a `mocpp_initialize(url, id, ...)`. Se implementó un check con `endsWith()` para asegurar que se agregue el separador `/` y el ID correctamente.

### L-010: Precaución con parámetros guardados en NVS (Preferences)
**Contexto:** Cambiamos el puerto de la URL en el código base (`.ino` y `.cpp`) y lo enviamos por OTA, pero el dispositivo seguía intentando conectar al puerto viejo.
**Causa:** `provisioning.getOcppUrl()` levantaba la URL vieja almacenada en la memoria flash (NVS) configurada originalmente mediante el Captive Portal. NVS tiene prioridad y NO se borra con los updates OTA.
**Regla/Solución temporal:** Para updates rápidos donde no se puede pedir al usuario que reconfigure el WiFi manual haciendo un Factory Reset, es válido hardcodear la lectura ignorando el NVS temporalmente (`globalOcppUrl = "ws://[IP]:8080/ws"`).

### L-011: Migración de Servidor via OTA y Sincronismo de NVS
**Contexto:** Al mover el servidor a la nueva IP `72.60.9.174:8080`, los cargadores en campo seguían intentando conectar a la IP vieja guardada en su memoria interna (NVS).
**Problema:** Una actualización OTA normal no sobreescribe los valores de `Preferences` (NVS) automáticamente a menos que se programe explícitamente.
**Solución:** Se implementó un "hard-override" en el `setup()` del `.ino` definiendo `globalOcppUrl = "ws://72.60.9.174:8080/ws"`. Esto garantiza que, tras el reboot post-OTA, el cargador use la IP correcta independientemente de lo que diga su memoria.
**Regla:** En migraciones críticas de infraestructura, el código debe forzar los parámetros de red nuevos durante al menos una versión completa de firmware antes de volver a confiar en los valores persistidos en NVS.

### L-012: ESP32 no conecta a iPhone Personal Hotspot
**Contexto:** El formulario de WiFi del captive portal acepta SSID/contraseña, pero el ESP32 falla al conectar cuando la red es un hotspot de iPhone.  
**Causas:** (1) iPhone emite en **5 GHz** por defecto → ESP32 solo soporta 2.4 GHz. (2) iPhone puede negociar **WPA3/PMF** que no es compatible con Arduino WiFi defaults. (3) El SSID del iPhone puede tener apóstrofes ("Juan's iPhone"). (4) iPhone **desactiva** el hotspot si se bloquea o se cierra la pantalla de Compartir Internet.  
**Solución firmware:** `WiFi.setAutoReconnect(true)` + `WiFi.setSleep(false)` + más reintentos (60 vs 40) + **NO borrar credenciales** al primer fallo (el hotspot puede haber hecho timeout temporal). Factory reset solo manual con botón BOOT 5s.  
**Regla:** Nunca hacer `clearCredentials()` automático en fallo de conexión WiFi — siempre reintentar. El hotspot del iPhone es inherentemente inestable.

### L-013: Calibración del Sensor de Corriente SCT-013
**Contexto:** Los valores reportados por el firmware para corriente y potencia activa diferían de los valores reales medidos por instrumental de medición físico (pinza amperométrica).
**Causa:** El convertidor ADC del ESP32-S3 usando atenuación de 11dB tiene no-linealidades, y los componentes físicos del acoplamiento (divisor resistivo, capacitores de filtrado) alteran el factor de ganancia real vs. el teórico del sensor SCT-013.
**Solución/Regla:** El factor de calibración `SCT_CALIBRACION` debe ajustarse empíricamente con cargas estables comparando la lectura del firmware contra la pinza. En este hardware se calibró finalmente en `47.2` para un consumo de 8.2 A (1800W @ 220V), logrando lecturas precisas.

### L-014: Duplicación del ID del cargador en la URL (MicroOcpp)
**Contexto:** La plataforma CPMS reportó que el cargador intentaba conectarse a una URL con el ID duplicado, por ejemplo: `/ws/JB260215130620/JB260215130620`.
**Causa:** La librería `MicroOcpp` concatena internamente y de forma automática el `chargeBoxId` al final de la ruta del `backendUrl` durante `mocpp_initialize()`. Al haber concatenado manualmente el ID a la variable `globalOcppUrl` en el firmware, se terminaba enviando el ID dos veces consecutivas.
**Regla:** Enviar siempre a `mocpp_initialize` la URL base sin el ID al final (ej: `ws://72.60.9.174:8080/ws`) y pasar el ID del cargador únicamente a través del segundo parámetro.


