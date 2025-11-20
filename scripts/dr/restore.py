#!/usr/bin/env python3
"""
Restore Script - 3dPot v2.0
Sprint 9: Disaster Recovery - Database and Critical Data Restore

Este script restaura backups do banco de dados PostgreSQL e dados críticos.
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


class RestoreError(Exception):
    """Exceção para erros de restore"""
    pass


class RestoreService:
    """Serviço de restore para DR"""
    
    def __init__(self, backup_dir: str = None):
        """
        Inicializa o serviço de restore
        
        Args:
            backup_dir: Diretório onde estão os backups
        """
        self.backup_dir = Path(backup_dir or os.getenv('BACKUP_DIR', './backups'))
        
        if not self.backup_dir.exists():
            raise RestoreError(f"Backup directory not found: {self.backup_dir}")
        
        # Database config from environment
        self.db_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.db_port = os.getenv('POSTGRES_PORT', '5432')
        self.db_name = os.getenv('POSTGRES_DB', '3dpot_dev')
        self.db_user = os.getenv('POSTGRES_USER', '3dpot')
        self.db_password = os.getenv('POSTGRES_PASSWORD', '3dpot123')
        
        # Storage paths
        self.storage_dir = Path(os.getenv('STORAGE_DIR', './storage'))
        
        logger.info(f"Restore service initialized. Backup dir: {self.backup_dir}")
    
    def list_available_backups(self) -> list:
        """
        Lista backups disponíveis
        
        Returns:
            list: Lista de dicionários com informações dos backups
        """
        manifests = sorted(
            self.backup_dir.glob("backup_manifest_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        backups = []
        for manifest_file in manifests:
            try:
                with open(manifest_file) as f:
                    manifest = json.load(f)
                backups.append({
                    "timestamp": manifest['timestamp'],
                    "date": manifest['backup_date'],
                    "manifest": str(manifest_file),
                    "total_size_mb": manifest['total_size_mb']
                })
            except Exception as e:
                logger.warning(f"Error reading manifest {manifest_file}: {e}")
        
        return backups
    
    def load_manifest(self, timestamp: str) -> dict:
        """
        Carrega manifesto de backup
        
        Args:
            timestamp: Timestamp do backup
            
        Returns:
            dict: Manifesto do backup
        """
        manifest_file = self.backup_dir / f"backup_manifest_{timestamp}.json"
        
        if not manifest_file.exists():
            raise RestoreError(f"Backup manifest not found: {manifest_file}")
        
        with open(manifest_file) as f:
            return json.load(f)
    
    def verify_backup_files(self, manifest: dict) -> bool:
        """
        Verifica se os arquivos de backup existem
        
        Args:
            manifest: Manifesto do backup
            
        Returns:
            bool: True se todos os arquivos existem
        """
        logger.info("Verifying backup files...")
        
        # Verifica DB backup
        if manifest['database']['backup_file']:
            db_file = Path(manifest['database']['backup_file'])
            if not db_file.exists():
                logger.error(f"Database backup file not found: {db_file}")
                return False
            logger.info(f"✓ Database backup found: {db_file}")
        
        # Verifica storage backup (opcional)
        if manifest['storage']['backup_file']:
            storage_file = Path(manifest['storage']['backup_file'])
            if not storage_file.exists():
                logger.warning(f"Storage backup file not found: {storage_file}")
            else:
                logger.info(f"✓ Storage backup found: {storage_file}")
        
        return True
    
    def restore_database(self, backup_file: Path, drop_existing: bool = False) -> bool:
        """
        Restaura banco de dados a partir de backup
        
        Args:
            backup_file: Caminho do arquivo de backup
            drop_existing: Se deve dropar o banco existente
            
        Returns:
            bool: True se restauração foi bem-sucedida
        """
        logger.info(f"Restoring database from: {backup_file}")
        
        if not backup_file.exists():
            raise RestoreError(f"Backup file not found: {backup_file}")
        
        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_password
        
        # Se drop_existing, primeiro dropa e recria o banco
        if drop_existing:
            logger.warning("Dropping existing database...")
            
            # Conecta ao banco postgres para dropar o banco de dados
            drop_cmd = [
                'psql',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', 'postgres',
                '-c', f'DROP DATABASE IF EXISTS {self.db_name}'
            ]
            
            try:
                subprocess.run(drop_cmd, env=env, check=True, capture_output=True)
                logger.info(f"Database {self.db_name} dropped")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to drop database: {e.stderr.decode()}")
                raise RestoreError("Failed to drop database")
            
            # Recria o banco
            create_cmd = [
                'psql',
                '-h', self.db_host,
                '-p', self.db_port,
                '-U', self.db_user,
                '-d', 'postgres',
                '-c', f'CREATE DATABASE {self.db_name}'
            ]
            
            try:
                subprocess.run(create_cmd, env=env, check=True, capture_output=True)
                logger.info(f"Database {self.db_name} created")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create database: {e.stderr.decode()}")
                raise RestoreError("Failed to create database")
        
        # Restaura usando pg_restore
        restore_cmd = [
            'pg_restore',
            '-h', self.db_host,
            '-p', self.db_port,
            '-U', self.db_user,
            '-d', self.db_name,
            '--clean' if not drop_existing else '--no-owner',
            '--if-exists',
            '--verbose',
            str(backup_file)
        ]
        
        try:
            result = subprocess.run(
                restore_cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Database restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            # pg_restore pode retornar exit code != 0 mesmo em restore parcial bem-sucedido
            # Verificamos se há erros críticos
            if "FATAL" in e.stderr or "ERROR" in e.stderr:
                logger.error(f"pg_restore failed with errors: {e.stderr}")
                raise RestoreError(f"Database restore failed: {e.stderr}")
            else:
                logger.warning("pg_restore completed with warnings (non-critical)")
                return True
        except FileNotFoundError:
            logger.error("pg_restore not found. Please install PostgreSQL client tools.")
            raise RestoreError("pg_restore not found")
    
    def restore_storage(self, backup_file: Path) -> bool:
        """
        Restaura arquivos de storage a partir de backup
        
        Args:
            backup_file: Caminho do arquivo tar.gz
            
        Returns:
            bool: True se restauração foi bem-sucedida
        """
        logger.info(f"Restoring storage from: {backup_file}")
        
        if not backup_file.exists():
            logger.warning(f"Storage backup file not found: {backup_file}")
            return False
        
        # Extrai tarball
        try:
            # Cria diretório pai se não existir
            self.storage_dir.parent.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                'tar',
                '-xzf',
                str(backup_file),
                '-C', str(self.storage_dir.parent)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("Storage restore completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"tar failed: {e.stderr}")
            raise RestoreError(f"Storage restore failed: {e.stderr}")
    
    def run_restore(self, timestamp: str, skip_storage: bool = False, 
                   drop_existing: bool = False, confirm: bool = False) -> dict:
        """
        Executa restore completo
        
        Args:
            timestamp: Timestamp do backup a restaurar
            skip_storage: Pular restore de storage
            drop_existing: Dropar banco existente antes de restaurar
            confirm: Confirmação para operação destrutiva
            
        Returns:
            dict: Informações do restore realizado
        """
        logger.info("=" * 60)
        logger.info("3dPot Restore Service - Starting restore process")
        logger.info("=" * 60)
        
        # Carrega manifesto
        manifest = self.load_manifest(timestamp)
        logger.info(f"Loaded backup manifest from {manifest['backup_date']}")
        
        # Verifica arquivos
        if not self.verify_backup_files(manifest):
            raise RestoreError("Backup files verification failed")
        
        # Confirmação para operações destrutivas
        if drop_existing and not confirm:
            logger.error("⚠️  DROP DATABASE requires --confirm flag!")
            raise RestoreError("Restore cancelled: --drop-existing requires --confirm")
        
        # Restore do banco de dados
        if manifest['database']['backup_file']:
            db_file = Path(manifest['database']['backup_file'])
            self.restore_database(db_file, drop_existing=drop_existing)
        else:
            logger.warning("No database backup in manifest")
        
        # Restore de storage (opcional)
        storage_restored = False
        if not skip_storage and manifest['storage']['backup_file']:
            storage_file = Path(manifest['storage']['backup_file'])
            storage_restored = self.restore_storage(storage_file)
        
        logger.info("=" * 60)
        logger.info("Restore completed successfully!")
        logger.info("=" * 60)
        
        return {
            "timestamp": timestamp,
            "restored_database": bool(manifest['database']['backup_file']),
            "restored_storage": storage_restored
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='3dPot Disaster Recovery - Restore Script'
    )
    parser.add_argument(
        '--backup-dir',
        default=None,
        help='Directory where backups are stored (default: ./backups)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available backups'
    )
    parser.add_argument(
        '--timestamp',
        help='Timestamp of backup to restore (e.g., 20250120_143000)'
    )
    parser.add_argument(
        '--skip-storage',
        action='store_true',
        help='Skip storage restore (database only)'
    )
    parser.add_argument(
        '--drop-existing',
        action='store_true',
        help='Drop existing database before restore (DESTRUCTIVE!)'
    )
    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Confirm destructive operations'
    )
    
    args = parser.parse_args()
    
    try:
        restore_service = RestoreService(backup_dir=args.backup_dir)
        
        # List backups
        if args.list:
            backups = restore_service.list_available_backups()
            
            if not backups:
                print("No backups found")
                return 0
            
            print("\n📦 Available backups:")
            print("-" * 80)
            for backup in backups:
                print(f"Timestamp: {backup['timestamp']}")
                print(f"Date: {backup['date']}")
                print(f"Size: {backup['total_size_mb']:.2f} MB")
                print(f"Manifest: {backup['manifest']}")
                print("-" * 80)
            
            return 0
        
        # Restore backup
        if not args.timestamp:
            print("Error: --timestamp is required for restore")
            print("Use --list to see available backups")
            return 1
        
        # Confirmação interativa para operações destrutivas
        if args.drop_existing and not args.confirm:
            print("\n⚠️  WARNING: This will DROP the existing database!")
            print("Use --confirm flag to proceed")
            return 1
        
        result = restore_service.run_restore(
            timestamp=args.timestamp,
            skip_storage=args.skip_storage,
            drop_existing=args.drop_existing,
            confirm=args.confirm
        )
        
        print("\n✅ Restore completed successfully!")
        print(f"Database restored: {result['restored_database']}")
        print(f"Storage restored: {result['restored_storage']}")
        
        return 0
        
    except RestoreError as e:
        logger.error(f"Restore failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.warning("Restore interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
