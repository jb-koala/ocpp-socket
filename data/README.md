# data/ — corridas registradas (etapa 9)

Una corrida = una carpeta `runs/AAAA-MM-DD_<nombre>/` con un archivo MCAP (un topic por señal:
temperatura, corriente, estado de sesión, mensajes OCPP) y un `meta.yml` (commit, placa, bench).

Los `.mcap` no se commitean (son grandes); se suben al store de logs. En git queda `meta.yml`
y un `summary.md` con los números que importan. Consultas en SQL con DuckDB:

```bash
pip install mcap duckdb
python data/query.py runs/2026-11-20_overtemp-01 "select max(temp_c), count(*) from temperature"
```
