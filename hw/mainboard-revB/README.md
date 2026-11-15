# mainboard rev B — diseño por bloques

Estado: **diseño definido, esquemático pendiente de dibujar en KiCad 10.** Este documento es la
especificación que se transcribe al esquemático; `pinout.md` es la asignación de GPIO. Cuando el
esquemático exista, este README pasa a ser la explicación de cada hoja.

Decisiones que lo definen: [0005](../../decisions/0005-modulo-wroom-en-placa-en-vez-de-devkit.md)
WROOM en placa · [0006](../../decisions/0006-medicion-clase-1-con-ic-dedicado.md) IC de medición ·
[0007](../../decisions/0007-alimentacion-buck-en-vez-de-7805.md) buck ·
[0009](../../decisions/0009-topologia-de-medicion-aislada.md) medición aislada ·
[0003](../../decisions/0003-corte-de-sesion-por-temperatura.md) corte por temperatura ·
[0004](../../decisions/0004-traba-de-tapa-solenoide-supercap.md) traba (pendiente de bench).

Requerimientos cubiertos: REQ003, REQ004, REQ005, REQ006, REQ007, REQ010, REQ011, REQ013.

## Regla de oro: dos mundos

```
 ┌───────────────── LADO RED (220 V) ─────────────────┐   ║   ┌──────── LADO SELV (3.3 V / 12 V) ────────┐
 │ TB1 → F1 → VR1 → L1 (CM) → X1/Y1 → K1 → SKT1       │   ║   │ ESP32-S3-WROOM-1  ·  ATM90E26  ·  buck    │
 │ PS1 primario · ZMCT102 primario · ZMPT101L primario │   ║   │ PS1 secundario · CT/VT secundarios · UI   │
 │ SW1 e-stop (en serie con la bobina de K1, 12 V) ─────────╫──→│ driver K1 · solenoide · NTC · expansión   │
 └────────────────────────────────────────────────────┘   ║   └────────────────────────────────────────────┘
                                       barrera: ≥ 6.4 mm creepage (reforzada, 250 V) + ranura fresada
```

Nada del lado SELV toca un nodo de red. Cruzan la barrera solo: PS1 (fuente aislada), ZMCT102 y
ZMPT101L (transformadores) y la bobina de K1 (relé con aislación reforzada bobina/contactos).

## Bloques

### 1. Entrada de red y protecciones — **se conserva de rev A** (probado 4 meses)

| Ref | Parte | Función |
|---|---|---|
| TB1 | Bornera 3P 9.5 mm con tapa (HB9500-9.5) | L / N / PE de entrada |
| F1 | Fusible 5×20 0.5 A T + clips | Protege solo el ramal auxiliar (PS1, transformadores). El camino de 10 A lo protege la térmica aguas arriba (instalación certificada, REQ014) |
| VR1 | Varistor S07K275 | Sobretensión, después del fusible |
| L1 | Choke modo común 2×10 mH | EMI |
| C2 | 100 nF X1 275 Vac | EMI entre L y N |
| C1, C5 | 2n2 Y1 3 kV | EMI L–PE, N–PE |
| PE | Pista ancha a TB1 y a SKT1 | Continuidad de tierra ≤ 0.1 Ω (ensayo de pre-compliance) |

### 2. Fuente auxiliar — **cambia** (0007)

| Ref | Parte | Notas |
|---|---|---|
| PS1 | HLK-10M12 (12 V, 10 W, 100–240 V in) | Se conserva. Aislación reforzada. 12 V alimenta bobina de K1 y solenoide |
| U3 | **Buck 12 V → 3.3 V, 2 A, SOT-23-6** (AP63203 o equivalente MP2451-class) | Reemplaza U1 7805 + HS1. Inductor 4.7 µH escudado, Cin 10 µF, Cout 22 µF ×2 |
| C4 | 470 µF 16 V en 12 V | Se conserva. Reserva para el pulso del solenoide |
| D4 | 1N4007 / SS14 | Protección inversa en entrada del buck |
| — | Fusible resettable 500 mA en 3V3 hacia el header de expansión | Un módulo con corto no tira el socket |

Consumo en reposo objetivo: < 1.3 W (PS1 en vacío ~0.4 W + WROOM Wi-Fi ~0.5 W + buck).

### 3. MCU — **cambia** (0005)

| Ref | Parte | Notas |
|---|---|---|
| U2 | **ESP32-S3-WROOM-1-N16R8** | Misma flash/PSRAM que el devkit de campo: el firmware y la partición `default_8MB` no cambian |
| J-USB | USB-C 16 pines, solo USB 2.0 | D+ → GPIO20, D− → GPIO19 (USB nativo del S3: flash y logs sin puente serie). CC1/CC2 con 5.1 kΩ a GND. ESD: USBLC6-2SC6 |
| SW-BOOT, SW-EN | Pulsadores táctiles SMD | BOOT a GPIO0 (pull-up 10 kΩ), EN con RC 10 kΩ / 1 µF |
| — | C 10 µF + 100 nF en 3V3 del módulo, pegados al pin | |
| — | Strapping: GPIO45 y GPIO46 libres (sin pull-up externo), GPIO3 libre | Ver `pinout.md` |
| J-DBG | Header 1×4: 3V3, GND, TX0 (GPIO43), RX0 (GPIO44) | Logs de boot aunque falle el USB |
| TP1–TP8 | Test points 1.5 mm para pogo pins | 3V3, GND, 12V, TX0, RX0, BOOT, EN, VBUS → fixture de fin de línea |

### 4. Potencia (relé) — **se conserva** + e-stop (REQ005)

| Ref | Parte | Notas |
|---|---|---|
| K1 | SFK112DM 20 A 250 Vac, bobina 12 V | Se conserva. Permite la variante 20 A con toma y cableado acordes |
| Q1 | BC817 + R base 1 kΩ + D flyback 1N4148 | Driver desde GPIO5. Pull-down 10 kΩ en base: relé abierto durante el boot |
| **SW1** | **Botón de emergencia NC (hongo)**, cableado por bornera 2P | **En serie con la bobina de K1 (12 V)**: al pulsar, el relé abre sin pasar por el MCU. Sin tensión de red en el botón → no necesita 16 A ni aislación reforzada |
| — | Sense de SW1 → GPIO42 vía divisor | El firmware lo reporta en OCPP (`StatusNotification` Faulted / `EmergencyStop`) |
| RC | Snubber 100 Ω + 100 nF X2 en paralelo a los contactos | Opcional, poblado según bench con cargadores Mode 2 (carga inductiva del contactor del vehículo) |

### 5. Medición — **cambia** (0006, 0009)

| Ref | Parte | Notas |
|---|---|---|
| U4 | **ATM90E26** (SSOP-28) + cristal 16.384 MHz | Interfaz: UART1 (GPIO17/18) a 9600 bps, modo elegido por pines MMD0/MMD1. SPI queda ruteada a test points por si hace falta |
| T1 | ZMCT102 (CT) | Se conserva. Burden ≈ 24 Ω (señal ≈ 120 mV rms a 10 A), filtro RC 1 kΩ / 33 nF diferencial a I1P/I1N |
| TR1 | ZMPT101L (VT) | Se conserva, con R4/R5 2×56 kΩ 0.5 W metal film en el primario y burden ≈ 100 Ω; filtro RC a V1P/V1N |
| — | Referencia 1.65 V no: el ATM90E26 tiene entradas diferenciales con referencia interna | Elimina el divisor de polarización de rev A |
| — | Calibración: registros de ganancia en NVS, cargados por el firmware. Se calibra por unidad en el fixture contra un patrón | REQ011 |

Alternativa de segundo proveedor (misma hoja, footprint distinto): BL0940 por UART, sin cristal.

### 6. Temperatura — **nuevo** (REQ003, REQ004)

| Ref | Parte | Notas |
|---|---|---|
| TH1 | NTC 10 kΩ β3950 encapsulado con cable, **sobre los bornes de SKT1** | Conector 2P (JST-XH). Divisor con 10 kΩ 1 % a 3V3 → GPIO1 (ADC1_CH0), C 100 nF |
| TH2 | NTC 10 kΩ SMD 0603 junto a K1 | Segundo punto: contactos del relé. GPIO2 (ADC1_CH1) |

Los umbrales (85 °C corte, 70 °C reanudar) están en `reqs/budgets.yml` y se generan al firmware.

### 7. Traba de tapa — **nuevo** (REQ006, 0004 pendiente de bench)

| Ref | Parte | Notas |
|---|---|---|
| Q5 | MOSFET N AO3400 + flyback SS14 | Driver del solenoide desde GPIO6, pull-down 10 kΩ |
| J-LOCK | Conector 3P: SOL+, SOL−, SENSE | Solenoide + microswitch de posición |
| SW-LOCK → GPIO7 | Microswitch NC/NO de posición de traba | `setConnectorPluggedInput` deja de ser `true` fijo |
| C-SC | **Footprint para supercapacitor 1 F / 5.5 V (o 2 × 2.7 V)** en el riel del solenoide, con diodo de bloqueo y R de carga | **No se puebla hasta que 0004 se acepte** con mediciones de bench |
| — | Detector de caída de 12 V: divisor + comparador (o el propio ADC) → GPIO21 | Dispara la liberación antes de que caiga el 3V3 |

### 8. Interfaz — **se conserva**

| Ref | Parte | Notas |
|---|---|---|
| PB1 | Pulsador iluminado RGB QN12-L1-RGB | Switch → GPIO4 (pull-down, HIGH = pulsado); LEDs R/G/B por BC817 desde GPIO38/39/40 con PWM |
| BZ1 | Buzzer 5 V con oscilador | Por BC817 desde GPIO41 (desde 12 V con R serie, o desde 3V3 si el modelo lo admite) |

### 9. Expansión — **cambia** a 2×8 (REQ007)

Header 2×8 2.54 mm, pinout en `pinout.md`: 3V3 (con fusible resettable), 5V **no** (no hay riel de 5 V;
se expone **12V** para LoRa/RFID que lo necesiten, con el módulo regulando), GND ×2, SPI (SCK/MOSI/MISO/CS),
I2C (SDA/SCL), UART2 (TX/RX), 2 GPIO (IRQ, RST). Cubre: SD (SPI), RFID RC522 (SPI), LoRa SX1276 (SPI+IRQ+RST),
segundo ESP32 (UART).

### 10. Mecánica / fabricación

- PCB 2 capas FR4 1.6 mm, cobre 2 oz en el camino de 10 A (o 1 oz con 6 mm de pista + estaño), 100 × 80 mm
  para seguir entrando en la caja GENROD 115×165×65 con la toma.
- Ranura fresada bajo PS1, T1, TR1 y K1 en la barrera. Creepage ≥ 6.4 mm, clearance ≥ 3 mm.
- Todo SMD salvo: K1, TB1, PS1, L1, C2/C1/C5 (X/Y), T1, TR1, C4, USB-C, headers. Lado SMD apto para JLCPCB
  assembly (parts de la biblioteca básica/extendida donde se pueda).
- Serigrafía: `S/N ________` + QR con el MAC, logo FLUXIO, polaridad de los conectores.
- Fiduciales ×3, panelizable 2×2.

## Qué queda fuera de rev B (a propósito)

- Secure boot / flash encryption: es firmware + efuse, no placa (REQ012, 0008).
- Variante 20 A: mismo PCB; cambian SKT1, cableado y pista. No se diseña una placa distinta.
- LoRa / RFID / SD: módulos sobre el header de expansión, no en la mainboard.

## Verificación antes de pedir

1. `make hw-check`: ERC y DRC a cero con las reglas de JLCPCB (`jlcpcb.kicad_dru`).
2. `pytest tests/`: BOM dentro de presupuesto, todas las partes con código LCSC.
3. Revisión humana de la barrera de aislación sobre el layout (checklist en `../README.md`).
4. 5 placas de prueba → bench térmico 10 A continuos, calibración de medición en 5 puntos,
   10 sesiones seguidas sin reinicio.
