#!/usr/bin/env bash
# Hook PreToolUse (Bash) de Claude Code: bloquea comandos que flashean o energizan hardware
# salvo que una persona haya exportado OCPP_ALLOW_FLASH=1 en la sesión.
# "A hook that blocks, not a sentence in the prompt" (etapa 8).
set -euo pipefail
input=$(cat)
cmd=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null || true)

pattern='(pio[[:space:]]+run.*-t[[:space:]]+upload|pio[[:space:]]+run.*--target[[:space:]]+upload|pio[[:space:]]+test[[:space:]]+-e[[:space:]]+esp32|esptool|idf\.py[[:space:]].*flash|probe-rs[[:space:]]+(run|download|flash)|openocd|dfu-util|make[[:space:]]+(flash|bench-test|bench-power))'

if printf '%s' "$cmd" | grep -Eq "$pattern"; then
  if [ "${OCPP_ALLOW_FLASH:-0}" != "1" ]; then
    cat <<MSG >&2
BLOQUEADO por .claude/hooks/block_flash.sh: el comando flashea o energiza hardware.
Lo ejecuta una persona, con el bench sin tensión de red, exportando OCPP_ALLOW_FLASH=1.
Comando: $cmd
MSG
    exit 2
  fi
fi
exit 0
