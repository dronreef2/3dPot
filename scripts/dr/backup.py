#!/usr/bin/env python3
"""
Backup Script - 3dPot v2.0
Sprint 9: Disaster Recovery - Database and Critical Data Backup

Este script realiza backup do banco de dados PostgreSQL e dados críticos
para recuperação em caso de desastre.
"""

import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime
from pathlib import Path
import json
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupError(Exception):
    """Exceção para erros de backup"""
    pass


class BackupService:
    """Serviço de backup para DR"""
    
    def __init__(self, backup_dir: str = None):
        """
        Inicializa o serviço de backup
        
        Args:
            backup_dir: Diretório para armazenar backups (padrão: ./backups)
        """
        self.backup_dir = Path(backup_dir or os.getenv('BACKUP_DIR', './backups'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database config from environment
        self.db_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.db_port = os.getenv('POSTGRES_PORT', '5432')
        self.db_name = os.getenv('POSTGRES_DB', '3dpot_dev')
        self.db_user = os.getenv('POSTGRES_USER', '3dpot')
        self.db_password = os.getenv('POSTGRES_PASSWORD', '3dpot123')
        
        # Storage paths
        self.storage_dir = Path(os.getenv('STORAGE_DIR', './storage'))
        
        logger.info(f"Backup service initialized. Backup dir: {self.backup_dir}")
    
    def check_disk_space(self, required_mb: int = 1000) -> bool:
        """
        Verifica se há espaço em disco suficiente
        
        Args:
            required_mb: Espaço necessário em MB
            
        Returns:
            bool: True se há espaço suficiente
        """
        stat = shutil.disk_usage(self.backup_dir)
        available_mb = stat.free / (1024 * 1024)
        
        logger.info(f"Available disk space: {available_mb:.2f} MB")
        
        if available_mb < required_mb:
            logger.error(f"Insufficient disk space. Required: {required_mb} MB, Available: {available_mb:.2f} MB")
            return False
        
        return True
    
    def backup_database(self, timestamp: str) -> Path:
        """
        Realiza backup do banco de dados PostgreSQL usando pg_dump
        
        Args:
            timestamp: Timestamp para nomear o arquivo
            
        Returns:
            Path: Caminho do arquivo de backup
        """
        logger.info("Starting database backup...")
        
        # Nome do arquivo de backup
        backup_file = self.backup_dir / f"db_backup_{timestamp}.sql"
        
        # Comando pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_password
        
        cmd = [
            'pg_dump',
            '-h', self.db_host,
            '-p', self.db_port,
            '-U', self.db_user,
            '-d', self.db_name,
            '-F', 'c',  # Custom format (compressed)
            '-f', str(backup_file),
            '--verbose'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Database backup completed: {backup_file}")
            logger.info(f"Backup size: {backup_file.stat().st_size / (1024*1024):.2f} MB")
            
            return backup_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"pg_dump failed: {e.stderr}")
            raise BackupError(f"Database backup failed: {e.stderr}")
        except FileNotFoundError:
            logger.error("pg_dump not found. Please install PostgreSQL client tools.")
            raise BackupError("pg_dump not found")
    
    def backup_storage(self, timestamp: str) -> Path:
        """
        Realiza backup de arquivos de armazenamento críticos
        
        Args:
            timestamp: Timestamp para nomear o arquivo
            
        Returns:
            Path: Caminho do arquivo tar.gz
        """
        logger.info("Starting storage backup...")
        
        if not self.storage_dir.exists():
            logger.warning(f"Storage directory not found: {self.storage_dir}")
            return None
        
        # Nome do arquivo de backup
        backup_file = self.backup_dir / f"storage_backup_{timestamp}.tar.gz"
        
        # Cria tarball compactado
        try:
            cmd = [
                'tar',
                '-czf',
                str(backup_file),
                '-C', str(self.storage_dir.parent),
                self.storage_dir.name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Storage backup completed: {backup_file}")
            logger.info(f"Backup size: {backup_file.stat().st_size / (1024*1024):.2f} MB")
            
            return backup_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"tar failed: {e.stderr}")
            raise BackupError(f"Storage backup failed: {e.stderr}")
    
    def create_backup_manifest(self, timestamp: str, db_backup: Path = None, 
                              storage_backup: Path = None) -> Path:
        """
        Cria manifesto JSON com informações do backup
        
        Args:
            timestamp: Timestamp do backup
            db_backup: Caminho do backup do banco
            storage_backup: Caminho do backup de storage
            
        Returns:
            Path: Caminho do arquivo de manifesto
        """
        manifest_file = self.backup_dir / f"backup_manifest_{timestamp}.json"
        
        manifest = {
            "timestamp": timestamp,
            "backup_date": datetime.now().isoformat(),
            "database": {
                "host": self.db_host,
                "port": self.db_port,
                "database": self.db_name,
                "backup_file": str(db_backup) if db_backup else None,
                "size_mb": db_backup.stat().st_size / (1024*1024) if db_backup else 0
            },
            "storage": {
                "backup_file": str(storage_backup) if storage_backup else None,
                "size_mb": storage_backup.stat().st_size / (1024*1024) if storage_backup else 0
            },
            "total_size_mb": (
                (db_backup.stat().st_size if db_backup else 0) +
                (storage_backup.stat().st_size if storage_backup else 0)
            ) / (1024*1024)
        }
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Backup manifest created: {manifest_file}")
        
        return manifest_file
    
    def cleanup_old_backups(self, keep_count: int = 7):
        """
        Remove backups antigos, mantendo apenas os N mais recentes
        
        Args:
            keep_count: Número de backups a manter
        """
        logger.info(f"Cleaning up old backups (keeping last {keep_count})...")
        
        # Lista todos os manifestos
        manifests = sorted(
            self.backup_dir.glob("backup_manifest_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Remove backups antigos
        for manifest_file in manifests[keep_count:]:
            try:
                # Lê o manifesto para saber quais arquivos deletar
                with open(manifest_file) as f:
                    manifest = json.load(f)
                
                # Remove arquivos de backup
                if manifest['database']['backup_file']:
                    db_file = Path(manifest['database']['backup_file'])
                    if db_file.exists():
                        db_file.unlink()
                        logger.info(f"Removed old DB backup: {db_file}")
                
                if manifest['storage']['backup_file']:
                    storage_file = Path(manifest['storage']['backup_file'])
                    if storage_file.exists():
                        storage_file.unlink()
                        logger.info(f"Removed old storage backup: {storage_file}")
                
                # Remove manifesto
                manifest_file.unlink()
                logger.info(f"Removed old manifest: {manifest_file}")
                
            except Exception as e:
                logger.error(f"Error cleaning up {manifest_file}: {e}")
    
    def run_backup(self, skip_storage: bool = False, keep_count: int = 7) -> dict:
        """
        Executa backup completo
        
        Args:
            skip_storage: Pular backup de storage
            keep_count: Número de backups a manter
            
        Returns:
            dict: Informações do backup realizado
        """
        logger.info("=" * 60)
        logger.info("3dPot Backup Service - Starting backup process")
        logger.info("=" * 60)
        
        # Verifica espaço em disco
        if not self.check_disk_space(required_mb=1000):
            raise BackupError("Insufficient disk space")
        
        # Timestamp para este backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup do banco de dados
        db_backup = self.backup_database(timestamp)
        
        # Backup de storage (opcional)
        storage_backup = None
        if not skip_storage:
            try:
                storage_backup = self.backup_storage(timestamp)
            except BackupError as e:
                logger.warning(f"Storage backup failed (non-critical): {e}")
        
        # Cria manifesto
        manifest = self.create_backup_manifest(timestamp, db_backup, storage_backup)
        
        # Cleanup de backups antigos
        self.cleanup_old_backups(keep_count)
        
        logger.info("=" * 60)
        logger.info("Backup completed successfully!")
        logger.info(f"Manifest: {manifest}")
        logger.info("=" * 60)
        
        return {
            "timestamp": timestamp,
            "db_backup": str(db_backup),
            "storage_backup": str(storage_backup) if storage_backup else None,
            "manifest": str(manifest)
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='3dPot Disaster Recovery - Backup Script'
    )
    parser.add_argument(
        '--backup-dir',
        default=None,
        help='Directory to store backups (default: ./backups)'
    )
    parser.add_argument(
        '--skip-storage',
        action='store_true',
        help='Skip storage backup (database only)'
    )
    parser.add_argument(
        '--keep',
        type=int,
        default=7,
        help='Number of backups to keep (default: 7)'
    )
    
    args = parser.parse_args()
    
    try:
        backup_service = BackupService(backup_dir=args.backup_dir)
        result = backup_service.run_backup(
            skip_storage=args.skip_storage,
            keep_count=args.keep
        )
        
        print("\n✅ Backup completed successfully!")
        print(f"Database: {result['db_backup']}")
        if result['storage_backup']:
            print(f"Storage: {result['storage_backup']}")
        print(f"Manifest: {result['manifest']}")
        
        return 0
        
    except BackupError as e:
        logger.error(f"Backup failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Backup interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
