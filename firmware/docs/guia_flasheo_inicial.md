# 🚀 Guía de Flasheo Inicial y Activación de OTA

Este documento detalla el procedimiento para realizar la primera instalación (flasheo por cable USB) del firmware en un dispositivo **ESP32-S3** nuevo, garantizando que el mapa de particiones de la memoria flash quede correctamente configurado para permitir futuras actualizaciones inalámbricas (OTA).

---

## ⚠️ Concepto Crítico: El Mapa de Particiones

El ESP32-S3 de este proyecto cuenta con **4MB de memoria flash**. 
* Si se flashea por primera vez usando el esquema de partición por defecto o uno inadecuado como `huge_app` (que asigna 3.1MB a la aplicación principal sin dejar particiones de respaldo), la **tabla de particiones física** del chip no reservará espacio para actualizaciones inalámbricas.
* Al no tener partición secundaria de respaldo, cualquier intento de actualización por OTA (Over-The-Air) fallará inmediatamente con `ERROR en la actualizacion`.
* **Regla de oro:** El primer flasheo por cable USB debe escribir en el chip la tabla de particiones **`min_spiffs`** (que divide la flash en dos particiones idénticas de ~1.9MB para permitir el intercambio en caliente del firmware).

---

## 🛠️ Requisitos de Software

Asegúrate de contar con la herramienta `arduino-cli` y el núcleo de ESP32 instalado en el sistema:

```bash
# Verificar instalación
arduino-cli version

# Asegurar soporte de placas esp32 (versión recomendada >= 2.0.11)
arduino-cli core update-index
```

---

## 📥 Paso 1: Compilación del Firmware

La compilación debe definir explícitamente el parámetro `PartitionScheme=min_spiffs`. 

Ejecuta el siguiente comando desde la raíz del proyecto para compilar y generar los binarios en el directorio `build/`:

```bash
arduino-cli compile \
  --fqbn esp32:esp32:esp32s3:PartitionScheme=min_spiffs \
  --output-dir build/esp32.esp32.esp32s3 \
  .
```

---

## 🔌 Paso 2: Flasheo por Cable USB (Primera Vez)

1. Conecta el **ESP32-S3** a tu computadora mediante un cable de datos USB.
2. Identifica el puerto serial asignado. En macOS suele tener el formato `/dev/cu.usbmodem*` o `/dev/cu.usbserial*`. Puedes listarlos con:
   ```bash
   arduino-cli board list
   ```
3. Ejecuta el comando de subida especificando el puerto detectado y forzando el mismo esquema de partición:

```bash
arduino-cli upload \
  -p /dev/cu.usbmodemXXXXXXXX \
  --fqbn esp32:esp32:esp32s3:PartitionScheme=min_spiffs \
  --input-dir build/esp32.esp32.esp32s3
```

*Una vez completado el flasheo, la tabla de particiones `min_spiffs` habrá quedado guardada físicamente en la dirección `0x8000` de la flash del chip.*

---

## 📶 Paso 3: Inicialización y Conexión WiFi

Al ser un micro nuevo sin credenciales almacenadas en su memoria interna (NVS):
1. El dispositivo iniciará automáticamente en modo **Access Point (AP)** y el LED RGB onboard parpadeará en color **blanco**.
2. Desde tu computadora o teléfono, conéctate a la red WiFi abierta: **`Fluxio-Setup`**.
3. Se abrirá una interfaz gráfica (Captive Portal) automáticamente. Si no lo hace, ingresa a la IP `192.168.4.1` en tu navegador.
4. Completa los campos:
   * **SSID y Password** de tu red WiFi local.
   * **OCPP Server URL** (ej: `ws://72.60.9.174:8080/ws`).
   * **ID del Cargador** (el por defecto es `OCCP-SOCKET-01`).
5. Presiona **Guardar y Conectar**. El ESP32 se reiniciará, guardará los datos de forma permanente y el LED brillará en **verde** una vez conectado a la red.

---

## 📡 Actualizaciones Futuras vía OTA (Sin Cables)

A partir de este momento, el dispositivo está listo para ser actualizado de forma inalámbrica por WiFi, **sin necesidad de volver a conectarlo por cable**.

Cuando compiles una nueva versión del firmware (incrementando el número en `Version.h`), sube el binario a través del servidor OTA embebido en el cargador (puerto `8266`) usando `curl`:

```bash
curl -X POST http://<IP_DEL_CARGADOR>:8266/update \
  -H "X-OTA-Pass: $OTA_HTTP_PASS" \
  -F "firmware=@build/esp32.esp32.esp32s3/occp-socket-charger.ino.bin" \
  --progress-bar
```

El dispositivo recibirá el binario en la partición secundaria, verificará el Hash, grabará el nuevo firmware y se reiniciará automáticamente corriendo la nueva versión.
