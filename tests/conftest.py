"""
Configuração global de fixtures para os testes do projeto 3dPot
"""

import os
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def project_root():
    """Fixture que retorna o diretório raiz do projeto."""
    return Path(os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def models_root():
    """Fixture que retorna o diretório de modelos 3D."""
    return Path(os.path.dirname(os.path.dirname(__file__))) / 'modelos-3d'

@pytest.fixture
def temp_dir():
    """Fixture que retorna um diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
