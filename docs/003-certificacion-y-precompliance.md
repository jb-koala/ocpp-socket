# Certificación y pre-compliance del OCPP Socket

Estado al 2026-11-15. Verificado contra fuentes públicas (lista al final). **No es asesoramiento
legal**: la clasificación del producto la decide el organismo de certificación en la consulta
inicial, y el marco cambió dos veces en los últimos 18 meses. Esto es el mapa para llegar a esa
consulta con las preguntas correctas y con un producto que pase.

## 1. Lo que cambió respecto del deck

El deck (slide 13) habla de "IRAM bajo esquema CB". La idea sigue valiendo, pero el marco legal no es
el que todos citan:

| Tema | Antes | Ahora |
|---|---|---|
| Seguridad eléctrica | Res. SC 169/2018 | **Derogada el 25-feb-2025** por la **Res. SIyC 16/2025**, que aprueba un nuevo Reglamento Técnico. Los certificados viejos valen 1 año desde esa fecha. Los nuevos **duran 2 años** |
| Certificados extranjeros | Había que re-certificar en el país | El nuevo régimen **acepta certificados internacionales reconocidos** (CB/IECEE) sin re-ensayar localmente cuando el producto ya cumple IEC |
| Homologación de radio (Wi-Fi) | Trámite ENACOM/RAMATEL de los años 80 | **Res. ENACOM 57/2026** (26-feb-2026, rige desde sep-2026): agencias de certificación privadas, registro por "familias de producto", homologación inmediata contra certificado de conformidad |
| Instalación | — | **AEA 90364-7-722 edición 2024**: sección específica para suministro a vehículos eléctricos en inmuebles |

Consecuencia práctica: **certificar primero bajo esquema CB (IECEE) con un laboratorio reconocido y
después registrar en Argentina es ahora el camino corto**, no el largo. Y el certificado CB es el que
viaja a Líbano y a cualquier otro mercado del deck.

## 2. La pregunta que define todo: ¿qué es el producto?

El OCPP Socket no es un cargador: es un **tomacorriente con control, medición y comunicación**. El
cargador Mode 2 (el cable con la cajita, IC-CPD según IEC 62752) lo pone el usuario. Según cómo lo
clasifique el organismo, aplican normas muy distintas:

| Clasificación | Normas | Qué implica |
|---|---|---|
| **A. Tomacorriente con dispositivo electrónico de control** (la que conviene defender) | IEC 60884-1 / IRAM 2071 (toma) + IEC 60669-2-1 (interruptores electrónicos) o IEC 60730-1 (controles automáticos) + IEC 62053-21 (medidor clase 1, si se factura) | Ensayos conocidos, laboratorios locales los hacen, sin pilot ni comunicación con el vehículo |
| **B. Equipo de alimentación de VE (EVSE) Mode 1/2** | IEC 61851-1 + IEC 61851-21-2 (EMC) | El Anexo de la Res. 16/2025 lista "cargadores de batería para vehículos eléctricos de carretera: IEC 61851 / IEC 62752". Si IRAM lo pone acá, piden función de control pilot, lo que el producto **no tiene ni debe tener** (eso está en el IC-CPD) |
| C. Aparato electrodoméstico | IEC 60335-1 | Poco probable, pero es el "cajón de sastre" |

**Argumento para A**, con la norma en la mano: IEC 61851-1 define Mode 2 como conexión a la red
mediante tomacorrientes normalizados, con el control y la protección en el cable (IC-CPD). El
tomacorriente no es parte del EVSE. El OCPP Socket agrega al tomacorriente un relé controlado, un
medidor y una traba; ninguna de esas funciones es "suministro de energía al VE" en el sentido de 61851.

Lo que hay que llevar a la consulta: este documento, el esquema de bloques de rev B, y la pregunta
escrita "¿bajo qué norma de producto evalúan un tomacorriente controlado con medición, destinado a
carga Mode 2?". Pedir la respuesta por escrito.

### El tomacorriente en sí: decisión pendiente (0010)

Rev A usa una "toma IP universal 10 A". Para una instalación fija en Argentina la AEA y las normas de
producto esperan **IRAM 2071** (10 A o 20 A). La Res. 16/2025 flexibilizó la geometría de las *fichas*
de los aparatos, no de los *tomacorrientes* de instalación. Una toma universal puede ser lo que trabe
la certificación aunque todo lo demás pase. Ver `decisions/0010-tipo-de-tomacorriente.md`.

## 3. Los cuatro trámites, en orden

```
 1. Consulta de alcance (IRAM u otro OC reconocido)   → clasificación por escrito, lista de normas, cotización
 2. Pre-compliance en casa + laboratorio               → el diseño pasa antes de gastar en el ensayo formal
 3. Ensayo formal CB (laboratorio CBTL) + certificado  → CB Test Certificate + Test Report
 4. Registros en Argentina                             → seguridad eléctrica (Res. 16/2025) con el CB,
                                                          ENACOM (Res. 57/2026) para el módulo Wi-Fi,
                                                          metrología si se factura por kWh (ver §5)
```

Organismos de certificación reconocidos para seguridad eléctrica (la lista oficial la publica la
Secretaría; los históricos son IRAM, INTI, UL de Argentina, TÜV Rheinland Argentina, Intertek, Lenor).
Conviene pedir cotización a dos.

## 4. Pre-compliance: qué ensayar antes de pagar el formal

Ordenado por "qué rompe más diseños". Lo que falla acá se corrige en rev B antes de pedir las 50.

| # | Ensayo | Norma de referencia | Criterio | Equipo | ¿En casa? |
|---|---|---|---|---|---|
| 1 | **Calentamiento a corriente nominal** | IEC 60884-1 §19 | 10 A continuos ≥ 1 h hasta estabilizar; elevación de temperatura en bornes y contactos ≤ 45 K | Carga resistiva 2.2 kW, termocuplas tipo K ×4 (bornes de toma, TB1, K1, ambiente), logger | **Sí.** Es el ensayo del riesgo #1 del deck. Se hace en `bench/` y queda en `data/runs/` |
| 2 | **Rigidez dieléctrica** | IEC 60884-1 §17 / IEC 61010 | Red ↔ SELV: 3 kV AC 1 min (reforzada) sin descarga; red ↔ PE: 1.5 kV | Hipot tester (≈ 5 kV AC) | Sí, con hipot. Es el que valida la barrera de 6.4 mm |
| 3 | **Resistencia de aislación** | idem | ≥ 5 MΩ a 500 V DC | Megóhmetro 500/1000 V | Sí |
| 4 | **Continuidad de tierra** | IEC 60884-1 §11 | ≤ 0.1 Ω entre PE de entrada y PE de la toma a 25 A | Ground bond tester (o fuente 25 A + mV) | Sí |
| 5 | **Corriente de fuga** | IEC 60335-1 §13 | ≤ 0.25 mA (clase I fijo, a tierra) | Medidor de fuga o red de medición + mV | Sí |
| 6 | **Distancias (creepage / clearance)** | IEC 60664-1 | ≥ 6.4 mm / ≥ 3 mm reforzada 250 V, grado de polución 2 | Calibre, lupa, el DRC de KiCad | Sí: `make hw-check` con `jlcpcb.kicad_dru` |
| 7 | **Resistencia al calor y al fuego** | IEC 60884-1 §28 (bola, hilo incandescente 850 °C en partes que sostienen partes con tensión) | Sin ignición sostenida | Hilo incandescente | **No.** Laboratorio. Afecta la elección de la **caja**: la GENROD tiene que tener su propio certificado; si no, se ensaya |
| 8 | **IP de la caja** | IEC 60529 | IP44 mínimo exterior; la caja GENROD declara IP65 | — | Certificado del fabricante de la caja |
| 9 | **Emisiones conducidas** | CISPR 14-1 / CISPR 32 clase B | 150 kHz–30 MHz bajo límite | LISN + analizador de espectro | Parcial (pre-scan con LISN de USD 300–600 y analizador). El buck de rev B es el sospechoso |
| 10 | **Emisiones radiadas** | idem, 30 MHz–1 GHz | | Cámara / OATS | **No.** Laboratorio |
| 11 | **Inmunidad: ESD, EFT, surge** | IEC 61000-4-2 / -4 / -5 | ±8 kV aire ESD; 1 kV EFT en red; 1 kV / 2 kV surge | Generadores | **No.** Laboratorio. El varistor + fusible + choke de rev A existen para esto |
| 12 | **Exactitud de medición** | IEC 62053-21 clase 1 | ±1 % en 5 puntos: 0.3, 1, 2, 5, 10 A; cos φ 1 y 0.5 | Medidor patrón clase 0.5 o mejor + carga variable | **Sí** (con patrón). Valida 0006/0009 y **el hallazgo P0-3 del firmware** (hoy < 2 A = 0) |
| 13 | **Endurancia del relé y la traba** | IEC 60884-1 §21 (5.000 ciclos con carga) | Sin soldadura de contactos | Bench automatizado | Sí, con `bench/` ciclando |
| 14 | **Radio** | ETSI EN 300 328 / FCC 15.247 | — | — | **No se ensaya**: el WROOM-1 tiene certificación modular; se presenta la del módulo (ver §5) |

Equipo mínimo para hacer 1–6, 12 y 13 en casa (cotizar; precios de referencia a verificar):
hipot tester, megóhmetro, ground-bond, 4 termocuplas + logger, carga resistiva regulable 2.5 kW,
medidor patrón de energía clase 0.5, fuente de laboratorio. Es la línea "test lab / EV test equipment"
del presupuesto del deck (USD 2.360–2.660): entra, si el hipot y el patrón se compran usados o se
alquilan.

## 5. Registros posteriores al CB

- **Seguridad eléctrica (Res. 16/2025):** certificado de un OC reconocido, basado en el CB Test Report.
  Marcado de conformidad en el producto. Vigencia 2 años → **ponerlo en el calendario de producto**.
- **ENACOM (Res. 57/2026):** el ESP32-S3-WROOM-1 tiene certificación modular (FCC/CE/IC). Bajo el
  nuevo régimen, se registra el producto en RAMATEL vía una agencia de certificación con el
  certificado del módulo; el número RAMATEL va en la etiqueta y en las publicaciones. **Esta es una de
  las razones de la decisión 0005**: con el DevKitC no hay módulo certificable.
- **Metrología legal:** si el socket **factura por kWh al usuario final**, puede caer bajo el régimen de
  medidores de energía (INTI/metrología legal, IEC 62053-21 clase 1 y verificación primitiva).
  Alternativa que usa parte del mercado: facturar "servicio de carga" por tiempo/sesión con el kWh
  como dato informativo, hasta tener el medidor verificado. **Pregunta para el abogado y para la
  consulta de alcance, no para el ingeniero.** El deck ya lo lista como riesgo ("energy resale rules").
- **Instalación (AEA 90364-7-722:2024):** no certifica el producto pero condiciona cómo se vende:
  circuito dedicado por punto de carga, protección diferencial 30 mA tipo A (o detección de CC 6 mA,
  que normalmente aporta el IC-CPD), tomacorriente IRAM. El manual de instalación tiene que decir esto
  y el instalador firmarlo: es el "certified installation is mandatory" del deck, con número de norma.

## 6. Qué cambia en el repo por esto

| Dónde | Cambio |
|---|---|
| `reqs/REQ014` | Actualizado a Res. 16/2025 + Res. ENACOM 57/2026 + AEA 722 |
| `reqs/REQ015` (nuevo) | Ensayo de calentamiento: ≤ 45 K en bornes a 10 A continuos |
| `reqs/REQ016` (nuevo) | Rigidez dieléctrica 3 kV red↔SELV, 1.5 kV red↔PE |
| `decisions/0010` (propuesta) | Tomacorriente IRAM 2071 vs universal |
| `hw/mainboard-revB/README.md` | Ya tiene la barrera de 6.4 mm y el DRC; sumar hilo incandescente a la selección de caja |
| `bench/` | Ensayos 1, 12 y 13 como scripts con registro en `data/runs/` |
| Deck slide 13 | Cambiar "IRAM bajo esquema CB" por "CB primero, registro local después (Res. 16/2025)" y citar ENACOM 57/2026 |

## 7. Preguntas abiertas (para la consulta de alcance)

1. Clasificación: ¿tomacorriente controlado (IEC 60884 + 60669-2-1) o EVSE (IEC 61851-1)?
2. ¿La toma universal es aceptable en un producto de instalación fija, o tiene que ser IRAM 2071?
3. ¿La caja GENROD trae certificado de hilo incandescente e IP, o hay que ensayarla con el producto?
4. ¿Facturar por kWh exige medidor verificado por metrología legal, o alcanza con clase 1 declarada?
5. ¿Costo y plazo del ensayo CB completo para la clasificación que resulte? (El deck lo tiene en blanco.)

## Fuentes

- Res. SIyC 16/2025 — nuevo Reglamento Técnico de Seguridad Eléctrica; deroga 169/2018:
  https://abogados.com.ar/novedades-sobre-el-reglamento-tecnico-de-equipamiento-electrico-resolucion-162025/36438 ·
  https://www.argentina.gob.ar/node/457899 ·
  https://beccarvarela.com/novedades/nuevas-normas-de-la-secretaria-de-comercio-y-direccion-nacional-de-reglamentos-tecnicos/
- Anexo con "cargadores de batería para vehículos eléctricos de carretera: IEC 61851 / IEC 62752":
  https://cira.org.ar/wp-content/uploads/anexo_7311373_2.pdf
- TÜV Rheinland, resumen del reemplazo de la 169/2018:
  https://www.tuv.com/regulations-and-standards/en/argentina-update-on-product-safety-certification-of-electrical-and-electronic-equipment-resolution-no-169-2018-repealed.html
- Res. ENACOM 57/2026 — nuevo régimen de homologación:
  https://www.marval.com/Publicacion/se-aprueba-nuevo-regimen-para-equipos-de-telecomunicaciones-17514?lang=es ·
  https://www.cira.org.ar/es/servicios/normativas-servicios/resolucion/resolucion-57-2026/
- AEA 90364-7-722 edición 2024 (índice público): https://surtidores.com.ar/wp-content/uploads/2026/08/AEA-90364-7-722-1.pdf
- Organismos de certificación reconocidos (lista histórica): https://argentina.gob.ar/sites/default/files/2018/02/productos_electricos.pdf
- IEC 61851-1 (definición de Mode 2 y relación con IEC 62752), texto de adopción pública:
  https://mici.gob.pa/wp-content/uploads/2026/07/CONSULTA-PUBLICA-Norma-Tecnica-DGNTI-IEC-61851-1.pdf
