BOARD ?= mainboard-revA
PY    ?= python3

.PHONY: check test fw-test fw-build limits hw-check hw-route fab bench-test reqs mech mech-test

check: limits test fw-test mech-test  ## todo lo que corre en CI

test:                             ## pytest: presupuestos, BOM, requerimientos
	$(PY) -m pytest tests/ -q

reqs:                             ## valida el árbol Doorstop
	cd reqs && doorstop

limits:                           ## regenera firmware/lib/session_guard/limits.h desde reqs/budgets.yml
	$(PY) firmware/scripts/gen_limits.py > /dev/null

fw-test: limits                   ## tests Unity en laptop
	cd firmware && pio test -e native

fw-build: limits                  ## build ESP-IDF (no flashea)
	cd firmware && pio run -e esp32s3

hw-check:                         ## ERC + DRC de todas las placas con esquemático
	@set -e; for d in hw/*/; do \
	  b=$$(basename $$d); \
	  if ls $$d/*.kicad_sch >/dev/null 2>&1; then \
	    echo "== $$b"; \
	    kicad-cli sch erc --exit-code-violations -o /tmp/$$b-erc.rpt $$d/$$b.kicad_sch; \
	    kicad-cli pcb drc --exit-code-violations -o /tmp/$$b-drc.rpt $$d/$$b.kicad_pcb; \
	  else echo "== $$b: sin esquemático, se saltea"; fi; \
	done

hw-route:                         ## Freerouting local sobre $(BOARD)
	kicad-cli pcb export specctra -o /tmp/$(BOARD).dsn hw/$(BOARD)/$(BOARD).kicad_pcb
	java -jar $(FREEROUTING_JAR) -de /tmp/$(BOARD).dsn -do /tmp/$(BOARD).ses -mp 10
	@echo "Importar /tmp/$(BOARD).ses desde KiCad (File > Import > Specctra Session) y revisar."

fab:                              ## gerbers, BOM y posiciones vía KiBot
	kibot -c fab/kibot.yaml -e hw/$(BOARD)/$(BOARD).kicad_sch -b hw/$(BOARD)/$(BOARD).kicad_pcb -d fab/out/$(BOARD)

bench-test:                       ## hardware real. Bloqueado por hook salvo OCPP_ALLOW_FLASH=1
	cd bench && pytest -q --target esp32s3 --embedded-services esp,idf --app-path ../firmware/.pio/build/esp32s3

mech:                             ## caja: exporta STL/STEP a mechanical/enclosure/out/ y regenera renders
	cd mechanical/enclosure && $(PY) enclosure.py && $(PY) render.py

mech-test:                        ## caja: interferencias, holguras, junta, traba, cama de impresión, masa
	$(PY) -m pytest mechanical/tests -q

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'
