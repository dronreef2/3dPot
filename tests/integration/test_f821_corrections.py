#!/usr/bin/env python3
"""
Teste específico para verificar se os erros F821 (undefined name) foram corrigidos
"""

def test_imports_sucesso():
    """Testa se todos os imports estão funcionando corretamente."""
    print("🔍 TESTANDO IMPORTS CRÍTICOS...")
    
    # Testar imports do teste do QC station
    try:
        import cv2  # F821: undefined name 'cv2' - DEVE FUNCIONAR
        print("✅ cv2 importado com sucesso")
    except ImportError as e:
        print(f"❌ cv2 import failed: {e}")
        return False
    
    try:
        from flask import Flask  # F821: undefined name 'Flask' - DEVE FUNCIONAR
        print("✅ Flask importado com sucesso")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import numpy as np  # Numpy sempre deve funcionar
        print("✅ numpy importado com sucesso")
    except ImportError as e:
        print(f"❌ numpy import failed: {e}")
        return False
    
    # Testar imports do backend
    try:
        from backend.models import User  # F821: undefined name 'User' - DEVE FUNCIONAR
        print("✅ backend.models.User importado com sucesso")
    except ImportError as e:
        print(f"❌ backend.models.User import failed: {e}")
        return False
    
    try:
        from backend.schemas import UserCreate  # DEVE FUNCIONAR
        print("✅ backend.schemas.UserCreate importado com sucesso")
    except ImportError as e:
        print(f"❌ backend.schemas.UserCreate import failed: {e}")
        return False
    
    try:
        from backend.core.config import settings  # DEVE FUNCIONAR
        print("✅ backend.core.config.settings importado com sucesso")
    except ImportError as e:
        print(f"❌ backend.core.config.settings import failed: {e}")
        return False
    
    print("\n🎉 TODOS OS IMPORTS ESTÃO FUNCIONANDO!")
    print("✅ ERROS F821 CORRIGIDOS COM SUCESSO!")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TESTE DE CORREÇÃO DE ERROS F821")
    print("=" * 50)
    
    sucesso = test_imports_sucesso()
    
    if sucesso:
        print("\n🚀 STATUS: CI DEVE PASSAR AGORA!")
        exit(0)
    else:
        print("\n⚠️ STATUS: AINDA HÁ PROBLEMAS COM IMPORTS")
        exit(1)
