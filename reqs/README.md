# reqs/ — requerimientos (Doorstop)

Un archivo YAML por requerimiento. `doorstop` mantiene los links y marca como sospechoso
todo lo que depende de un requerimiento que cambió.

```bash
pip install doorstop
doorstop            # valida el árbol
doorstop add REQ    # crea el próximo REQnnn.yml
doorstop publish all docs/reqs.html
```

`budgets.yml` son los números duros del producto. Los lee `tests/test_budgets.py` y el firmware
(los umbrales de seguridad se generan a `firmware/lib/session_guard/limits.h` con `make limits`).
