"""Etapa 8: la placa imprime el commit al bootear; se verifica primero."""
import subprocess

import pytest


@pytest.mark.esp32s3
def test_boot_commit_matches_head(dut):
    head = subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"]).decode().strip()
    m = dut.expect(r"ocpp-socket fw commit=([0-9a-f]{12})(-dirty)? version=", timeout=20)
    assert m.group(1).decode() == head, "la placa corre otro commit; reflashear antes de seguir"
    assert not m.group(2), "build dirty en la placa: commiteá antes de medir"
    dut.expect("READY", timeout=10)
