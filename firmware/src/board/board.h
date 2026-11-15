// Board selection. Exactly one BOARD_* must be defined in platformio.ini build_flags.
// Hardware-specific pins live in one header per board; the .ino never hardcodes a GPIO.
#pragma once

#if defined(BOARD_DEVKIT_PROTO)
#include "board_devkit_proto.h"
#elif defined(BOARD_FLUXIO_PCB01)
#include "board_fluxio_pcb01.h"
#else
#error "Define BOARD_DEVKIT_PROTO or BOARD_FLUXIO_PCB01 in platformio.ini build_flags"
#endif
