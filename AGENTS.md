# Reglas de trabajo para el agente (CLAUDE.md / AGENTS.md)

Este repo está pensado para que un agente de IA haga ingeniería de hardware y firmware
junto con una persona. Las reglas de abajo no son sugerencias: son el contrato.

## 1. Todo es texto en Git

- Markdown para docs, YAML para requerimientos y BOM, KiCad 10 (texto) para electrónica,
  código Python/C para todo lo demás. Nada binario propietario.
- Antes de tocar algo, leé [README.md](README.md) (índice) y la carpeta que corresponda.
- Si cambiás algo que afecta a otra carpeta (ej. un pin en `hw/` que usa `firmware/`), actualizá las
  dos y anotalo en `CHANGELOG.md`.

## 2. Los docs se actualizan mientras trabajás

- Cada cambio de diseño con alternativas razonables → un archivo nuevo en `decisions/` (MADR).
  Las decisiones no se editan: si cambia, se crea una nueva que supersede a la anterior.
- Cada requerimiento nuevo o cambiado → `reqs/` vía Doorstop (`doorstop add REQ` / editar el YAML).
  Si un cambio rompe un requerimiento existente, se discute antes de tocar el código.
- `CHANGELOG.md` se escribe en cada PR, no al final.

## 3. Cada etapa tiene un chequeo que no podés editar para que pase

| Etapa | Chequeo | Comando |
|---|---|---|
| Requerimientos / presupuestos | masa, potencia y costo ≤ presupuesto | `pytest tests/` |
| Electrónica | ERC + DRC sin violaciones | `make hw-check` |
| BOM | toda parte con código de pedido y datos de masa/costo | `pytest tests/test_bom.py` |
| Firmware | tests Unity en laptop (native) | `make fw-test` |
| Hardware real | pytest-embedded espera la línea de ready | `make bench-test` |

Si un test falla, el fix va al diseño o al requerimiento (con decisión registrada), **nunca** al test
ni a los umbrales para que pase. Modificar `tests/`, `reqs/budgets.yml` o los límites de DRC
requiere una decisión en `decisions/` y aprobación humana explícita.

## 4. Lo que requiere a una persona

Estas acciones las ejecuta la persona, nunca el agente:

- Pagar un carrito (JLCPCB, Mouser, etc.). El agente prepara el carrito y se detiene.
- Flashear una placa conectada a hardware de potencia (relé, contactor, 220 V). El hook en
  `.claude/settings.json` bloquea `pio run -t upload`, `esptool`, `probe-rs` y `idf.py flash`
  salvo que la persona exporte `OCPP_ALLOW_FLASH=1` en esa sesión.
- Energizar el bench con tensión de red.
- Cambiar un umbral de seguridad (temperatura de corte, corriente máxima).

## 5. Reglas de firmware

- La lógica de negocio (máquina de estados de sesión, guardas de temperatura, parsing OCPP)
  vive en `firmware/lib/` sin dependencias de ESP-IDF, para que corra en laptop.
- Todo lo que depende del hardware vive en `firmware/src/` detrás de una interfaz chica.
- Escalera de tests: `native` (laptop) → placa de desarrollo → placa real. No se salta un escalón.
- Al bootear, el firmware imprime el hash de commit. Antes de interpretar un log, verificá que
  el commit que bootea sea el que creés que es.

## 6. Reglas de debugging

- Reproducí el bug con un test o una corrida registrada **antes** de arreglarlo.
- Un fix tiene que fallar en el build viejo y pasar en el nuevo.
- Para encontrar el commit que rompió algo: `git bisect run <test>`.

## 7. Convenciones

- Idioma de docs y commits: español rioplatense. Código, identificadores y comentarios de código: inglés.
- Commits chicos, un tema por commit. Mensaje: `<área>: <qué cambió>` (ej. `fw: add temperature guard`).
- Unidades siempre explícitas (`"250 g"`, `"3.3 V"`). Nunca números sueltos en YAML.
