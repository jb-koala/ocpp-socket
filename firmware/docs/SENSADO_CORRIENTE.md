# Especificación Técnica — Sensado de Corriente (SCT-013-030)

## 1. Librería y API Utilizada

**No se utiliza ninguna librería externa** (como `EmonLib`) para la lectura analógica. La medición está implementada de forma nativa utilizando las funciones del core de **Arduino-ESP32** (`analogRead`, `analogReadResolution`, `analogSetPinAttenuation`) junto con un algoritmo propio de cálculo **True-RMS de dos pasadas** en la función `medirIrms()`.

---

## 2. Configuración del ADC y Hardware

- **Sensor:** Transformador de corriente no invasivo **SCT-013-030** (salida en tensión: `0–1 Vrms` a `30 A`).
- **Pin de lectura:** `GPIO 6` (`ADC1_CH5`). Se utiliza específicamente el **ADC1** ya que el ADC2 del ESP32-S3 comparte recursos con el módulo WiFi y sufre interferencias durante la transmisión de red.
- **Resolución:** **12 bits** (`0` a `4095` cuentas) configurada mediante `analogReadResolution(12)`.
- **Atenuación:** **`ADC_11db`** configurada mediante `analogSetPinAttenuation(PIN_SCT, ADC_11db)`.

```cpp
// Configuración en setup()
analogReadResolution(12);                   // ADC 12-bit (0–4095)
analogSetPinAttenuation(PIN_SCT, ADC_11db); // Rango 0–3.3V para SCT-013
```

---

## 3. Algoritmo de Muestreo y Cálculo True-RMS

En lugar de utilizar un filtro digital recursivo, se emplea un **algoritmo de captura en buffer y doble pasada**, lo que evita tiempos de estabilización y elimina cualquier deriva del punto medio DC en cada lectura:

1. **Captura en ráfaga (Pasada 1):**
   - Toma **`1480` muestras** (`SCT_NUM_MUESTRAS`) espaciadas cada `100 µs` (`delayMicroseconds(100)`).
   - Esto conforma una ventana de captura de **`~148 ms`**, abarcando **`~7.4 ciclos completos`** de la onda de `50 Hz` (a razón de `~200 muestras por ciclo`), y acumula la suma total para obtener el valor medio exacto de esa ventana.
2. **Eliminación del Offset DC y Cálculo RMS (Pasada 2):**
   - Calcula el punto medio real (`media`) del divisor resistivo de polarización (`~1.65 V`) durante esa ventana puntual, anulando cualquier deriva térmica o variación de la fuente de `3.3 V`.
   - Recorre el vector de muestras restando la `media` a cada valor, eleva al cuadrado, promedia y aplica la raíz cuadrada:

$$\text{I}_{\text{RMS}} = \sqrt{\frac{1}{N}\sum_{i=1}^{N} (\text{ADC}_i - \text{media})^2} \times \left(\frac{3.3}{4096.0}\right) \times \text{SCT\_CALIBRACION}$$

3. **Frecuencia de actualización:**
   - Se ejecuta cada **`5 segundos`** (`SCT_INTERVAL = 5000`), lo que representa un ciclo de trabajo (*duty cycle*) de solo `~3%` del tiempo de CPU.

### Implementación en código

```cpp
#define PIN_SCT           6      // GPIO6 — ADC1_CH5
#define SCT_NUM_MUESTRAS  1480   // ~148ms de captura → ~7.4 ciclos a 50Hz
#define SCT_UMBRAL_A      2.0    // Umbral de ruido ambiental (A) — suprimir EMI
#define SCT_INTERVAL      5000   // Intervalo entre mediciones (ms)
float SCT_CALIBRACION = 47.2f;   // Cargado desde NVS al arrancar (default: 47.2)

double medirIrms() {
  long sumaADC = 0;
  for (int i = 0; i < SCT_NUM_MUESTRAS; i++) {
    _sctMuestras[i] = (uint16_t)analogRead(PIN_SCT);
    sumaADC += _sctMuestras[i];
    delayMicroseconds(100);
  }
  double media = (double)sumaADC / SCT_NUM_MUESTRAS;
  double sumaCuadrados = 0.0;
  for (int i = 0; i < SCT_NUM_MUESTRAS; i++) {
    double d = (double)_sctMuestras[i] - media;
    sumaCuadrados += d * d;
  }
  double irms = sqrt(sumaCuadrados / SCT_NUM_MUESTRAS) * (3.3 / 4096.0) * SCT_CALIBRACION;
  raw_corriente_A = (float)irms;
  return (irms < SCT_UMBRAL_A) ? 0.0 : irms;
}
```

---

## 4. Rango Admisible, Calibración y Precisión

| Parámetro | Valor / Especificación | Detalle |
| :--- | :--- | :--- |
| **Rango lineal del ADC (`11 dB`)** | `~0.10 V` a `3.10 V` | Conversión matemática sobre fondo de escala nominal de `3.3 V`. |
| **Excursión de señal a `30 Arms`** | `0.236 V` a `3.064 V` | Con punto medio en `1.65 V` y salida del sensor de `1 Vrms` (`±1.414 Vpico`), opera dentro de la zona lineal sin recorte (*clipping*) hasta **`30 Arms`** (`6.6 kW` a `220 V`). |
| **Factor de calibración (`SCT_CALIBRACION`)** | `47.2` (default) | Configurable desde el portal cautivo WiFi y almacenado en memoria NVS. Compensa las tolerancias del circuito de acondicionamiento y la respuesta del ADC. |
| **Resolución por bit (LSB)** | `~0.038 A` (`38 mA`) | Calculado como `(3.3 V / 4096) × 47.2`. |
| **Umbral de supresión de ruido (`SCT_UMBRAL_A`)** | `2.0 A` | Lecturas inferiores a `2.0 A` se reportan como `0.0 A` para filtrar ruido electromagnético (EMI) en reposo. El valor crudo sin filtrar se expone igualmente en `/status` como `raw_corriente_A`. |
| **Precisión práctica** | `±2%` a `±3%` | En el rango operativo de carga de un vehículo eléctrico (`6 A` a `30 A`), combinando la tolerancia del SCT-013 (`±1%`) y la linealidad del ADC calibrado. |
