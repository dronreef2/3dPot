# Exportes para facilitar importações
from .auth_service import AuthenticationService
from .conversational_service import ConversationalService
from .minimax_service import MinimaxService
from .budgeting_service import BudgetingService

# Sprint 6+ Services
from .print3d_service import Print3DService
from .collaboration_service import CollaborationService
# from .marketplace_service import MarketplaceService  # Temporariamente comentado
from .cloud_rendering_service import CloudRenderingService

# Importações condicionais para services com dependências opcionais
MODELING_AVAILABLE = False
SIMULATION_AVAILABLE = False

try:
    from .modeling_service import ModelingService
    MODELING_AVAILABLE = True
except ImportError:
    print("⚠️  ModelingService não disponível (cadquery/trimesh não instalados)")

try:
    from .simulation_service import SimulationService
    SIMULATION_AVAILABLE = True
except ImportError:
    print("⚠️  SimulationService não disponível (pybullet/numpy não instalados)")

# Lista de exports dinâmica
__all__ = [
    "AuthenticationService",
    "ConversationalService", 
    "MinimaxService",
    "BudgetingService",
    # Sprint 6+ Services
    "Print3DService",
    "CollaborationService",
    # "MarketplaceService",  # Temporariamente comentado
    "CloudRenderingService"
]

if MODELING_AVAILABLE:
    __all__.append("ModelingService")

if SIMULATION_AVAILABLE:
    __all__.append("SimulationService")