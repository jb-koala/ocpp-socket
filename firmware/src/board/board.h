// Board selection. Exactly one BOARD_* must be defined in platformio.ini build_flags.
// Hardware-specific pins live in one header per board; the .ino never hardcodes a GPIO.
#pragma once

#if defined(BOARD_DEVKIT_PROTO)
#include "board_devkit_proto.h"
#elif defined(BOARD_FLUXIO_PCB01)
#include "board_fluxio_pcb01.h"
#elif defined(BOARD_FLUXIO_REVB)
#include "board_fluxio_revb.h"
#else
#error "Define BOARD_DEVKIT_PROTO, BOARD_FLUXIO_PCB01 or BOARD_FLUXIO_REVB in platformio.ini build_flags"
#endif
