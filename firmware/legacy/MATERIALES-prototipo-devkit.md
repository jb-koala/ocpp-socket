# Lista de Materiales (BOM) - OCCP Socket Charger

A continuación se detalla la lista de componentes principales y secundarios necesarios para el ensamblaje del hardware del cargador inteligente.

## Componentes Principales

| Cantidad | Componente | Descripción / Especificaciones |
| :---: | :--- | :--- |
| **1** | **Placa de Desarrollo ESP32-S3** | DevkitC1 N16R8, WiFi + Bluetooth, 16MB Flash, 8MB PSRAM. Es el "cerebro" del equipo que maneja la lógica y la conexión OCPP. |
| **1** | **Sensor de Corriente Inductivo** | SCT-013-030. Pinza amperimétrica no invasiva, rango 30A, salida 1V. Mide el consumo eléctrico. |
| **1** | **Módulo Relay 1 Canal 5V** | Optoacoplado, Trigger High/Low para Arduino/ESP8266. Encargado de habilitar o cortar el paso de los 220V. |
| **1** | **Fuente Switching AC/DC** | Entrada 220V AC, Salida 5V 2A DC (Step Down). Alimenta al ESP32, el módulo relé y componentes de bajo voltaje desde la red eléctrica. |
| **1** | **Enchufe Impermeable Exterior** | IP66, 16A, Resistente a la intemperie. Es el tomacorriente final donde el usuario conectará el cargador de su vehículo u otro dispositivo. |

---

## Componentes Secundarios y Electrónica Menor (Acondicionamiento)

Para la interconexión en protoboard o el armado de la PCB final, también se requieren los siguientes componentes electrónicos pasivos y de interfaz:

| Cantidad | Componente | Descripción |
| :---: | :--- | :--- |
| **1** | **LED RGB NeoPixel** | Modelo WS2812B (direccional). Para indicar los distintos estados visuales del cargador (conectando, cargando, error). |
| **2** | **Pulsadores (Push Buttons)** | Botones momentáneos. Uno para el botón de acción (Touch) y otro para el botón de BOOT/Reset del sistema. |
| **1** | **Conector Jack 3.5mm o Bornera** | Para facilitar la conexión de la ficha del sensor SCT-013-030 a la placa. |
| **1** | **Capacitor Electrolítico 47µF** | Utilizado para el acoplamiento y filtrado en el circuito acondicionador (offset) del sensor de corriente. |
| **2** | **Resistencias** | De 10kΩ o 100kΩ. Para crear el divisor de voltaje (offset a 1.65V) necesario para que el ESP32 pueda leer el sensor SCT-013 de corriente alterna de manera segura. |
| **-** | **Borneras / Terminal Blocks** | Borneras de tornillo para conectar de forma segura los cables de 220V (entrada de red y salida hacia el enchufe IP66). |
