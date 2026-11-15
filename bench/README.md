# bench/ — pruebas en hardware real (etapa 8)

Banco: placa real + fuente de laboratorio (5 V para el MCU) + carga resistiva en la salida del relé
+ calentador controlado sobre el NTC. **La tensión de red se conecta solo con una persona presente.**

```
bench/
  conftest.py          fixtures pytest-embedded (puerto serie, flash)
  test_boot.py         espera "ocpp-socket fw commit=<hash>" y "READY"; falla si el commit no es HEAD
  test_overtemp.py     calienta el NTC y verifica que el relé abra dentro de temp_hold (REQ004)
  runs/                cada corrida se guarda como MCAP en data/runs/ (etapa 9)
```

```bash
pip install pytest-embedded pytest-embedded-serial-esp pytest-embedded-idf
OCPP_ALLOW_FLASH=1 make bench-test     # bloqueado sin la variable
```

El commit que imprime la placa al bootear se compara contra `git rev-parse HEAD` **antes** de
interpretar cualquier otra salida.
