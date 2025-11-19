#!/usr/bin/env python3
"""
Permite executar a CLI como módulo: python -m scripts.cli
"""

from .main import main

if __name__ == '__main__':
    import sys
    sys.exit(main())
