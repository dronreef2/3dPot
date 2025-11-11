"""
Configuração do Banco de Dados - 3dPot v2.0
SQLAlchemy setup com configurações otimizadas
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from core.config import settings
from models import Base

logger = logging.getLogger(__name__)

# Engine do banco otimizado para PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    
    # Pool settings para melhor performance
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    
    # PostgreSQL specific settings
    connect_args={
        "connect_timeout": 60,
        "options": "-c timezone=UTC"
    },
    
    # Logging
    echo=False,  # Set to True for SQL debugging
    echo_pool=False,
    
    # Future settings
    future=True
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def create_tables():
    """Cria todas as tabelas no banco"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise

def drop_tables():
    """Remove todas as tabelas (para desenvolvimento)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Tabelas removidas com sucesso")
    except Exception as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        raise

def get_db() -> Session:
    """
    Dependency para obter sessão do banco
    Usar como: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session():
    """
    Generator para obter sessão do banco
    Usar como: with get_db_session() as db:
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_connection():
    """Testa conexão com o banco"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            logger.info("Conexão com banco testada com sucesso")
            return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False

def health_check():
    """Health check do banco"""
    try:
        with engine.connect() as conn:
            # Teste básico
            conn.execute("SELECT 1")
            
            # Informações do banco
            result = conn.execute("""
                SELECT 
                    version(),
                    current_database(),
                    current_user
            """)
            db_info = result.fetchone()
            
            return {
                "status": "healthy",
                "database": {
                    "version": db_info[0] if db_info else "Unknown",
                    "name": db_info[1] if db_info else "Unknown",
                    "user": db_info[2] if db_info else "Unknown"
                },
                "connection_pool": {
                    "size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow(),
                    "invalid": engine.pool.invalid()
                }
            }
    except Exception as e:
        logger.error(f"Erro no health check do banco: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Context manager para transações
from contextlib import contextmanager

@contextmanager
def transaction(db: Session):
    """Context manager para transações automáticas"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Erro na transação: {e}")
        raise

@contextmanager  
def read_only_transaction(db: Session):
    """Context manager para transações de leitura"""
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na transação de leitura: {e}")
        raise

# Funções de utilidade para queries comuns
def get_user_by_email(db: Session, email: str):
    """Busca usuário por email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Busca usuário por username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id):
    """Busca usuário por ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_active_users_count(db: Session):
    """Conta usuários ativos"""
    return db.query(User).filter(User.is_active == True).count()

def cleanup_expired_sessions(db: Session):
    """Remove sessões expiradas do banco"""
    from datetime import datetime
    from models import RefreshToken
    
    deleted_count = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    
    logger.info(f"Removidas {deleted_count} sessões expiradas")
    return deleted_count

# Database events
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurações específicas para SQLite (desenvolvimento)"""
    if 'sqlite' in str(engine.url):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Configuração de logging SQL (desenvolvimento)
def enable_sql_logging():
    """Habilita logging de SQL (apenas para desenvolvimento)"""
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

# Exportar engine e SessionLocal
__all__ = [
    'engine', 
    'SessionLocal', 
    'get_db', 
    'get_db_session',
    'create_tables',
    'drop_tables',
    'test_connection',
    'health_check',
    'transaction',
    'read_only_transaction',
    'get_user_by_email',
    'get_user_by_username', 
    'get_user_by_id',
    'get_active_users_count',
    'cleanup_expired_sessions'
]