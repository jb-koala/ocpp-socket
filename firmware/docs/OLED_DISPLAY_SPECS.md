# Especificaciones y Conexionado de Pantalla OLED (SSD1306 I2C)

Este documento detalla la integración de hardware y la configuración de pines para la pantalla OLED de 128x64 píxeles (basada en el controlador SSD1306) en el cargador **Fluxio OCCP Socket Charger**.

## 1. Conexiones de Hardware (Cableado)

El módulo de pantalla OLED se conecta al microcontrolador ESP32-S3 mediante el bus **I2C**.

| Pin OLED | Pin ESP32-S3 | Descripción | Notas |
|:---:|:---:|:---|:---|
| **VCC** | **3.3V** | Alimentación del módulo | **No conectar a 5V** para proteger el nivel lógico del bus I2C. |
| **GND** | **GND** | Masa común | |
| **SDA** | **GPIO 8** | Línea de Datos Seriales I2C | Requiere resistencia pull-up externa de 4.7kΩ a 3.3V si el módulo no la tiene. |
| **SCL** | **GPIO 9** | Línea de Reloj Serial I2C | Requiere resistencia pull-up externa de 4.7kΩ a 3.3V si el módulo no la tiene. |

---

## 2. Diagrama de Conexionado del Bus I2C

```
             ESP32-S3                                OLED (SSD1306)
        +-----------------+                        +----------------+
        |            3.3V |------------------------| VCC            |
        |                 |      +-----------+     |                |
        |          GPIO 8 |------|---[4.7k]---+----| SDA            |
        |    (SDA)        |      | (Pull-Up)  |    |                |
        |          GPIO 9 |---+--|---[4.7k]---+----| SCL            |
        |    (SCL)        |   |  |            |    |                |
        |             GND |---|--|------------|----| GND            |
        +-----------------+   |  +-----------+    +----------------+
                              +-- (Alimentado a 3.3V)
```

---

## 3. Arquitectura del Software (Visualización)

El firmware utiliza la librería **U8g2** en modo *Page Buffer* (`U8G2_R0` con búfer de 128 bytes por línea o búfer completo de página si la RAM lo permite). Esto minimiza el consumo de memoria dinámica del ESP32-S3.

### Ciclos de Pantalla y Salvapantallas (Burn-In Protection)
Para evitar el desgaste y quemado prematuro de los píxeles OLED:
1. **Apagado Automático (Screen Timeout):** La pantalla se apaga tras **3 minutos (180 segundos)** de inactividad si no hay ninguna transacción de carga en curso.
2. **Despertar Automático:** La pantalla se enciende instantáneamente si:
   - Se presiona el pulsador físico de carga.
   - Cambia el estado del cargador (ej. se inicia una transacción remota desde el CPMS, se conecta el cable, etc.).
   - Se detecta una variación de consumo mayor a 0.5A en el sensor SCT-013.
   - El dispositivo se reinicia o se conecta/desconecta de la red WiFi.
