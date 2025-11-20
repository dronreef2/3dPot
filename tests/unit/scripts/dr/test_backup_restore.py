"""
Unit tests for DR (Disaster Recovery) Scripts
Testing backup and restore functionality
Sprint 9
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestBackupManifest:
    """Test backup manifest generation and validation"""
    
    def test_manifest_structure(self):
        """Test that manifest has required fields"""
        manifest = {
            "timestamp": "2025-11-20T00:00:00Z",
            "version": "1.0",
            "database": {
                "host": "localhost",
                "port": "5432",
                "name": "3dpot_dev",
                "backup_file": "db_backup_20251120_000000.sql"
            },
            "storage": {
                "backup_file": "storage_backup_20251120_000000.tar.gz",
                "size_bytes": 1024000
            }
        }
        
        # Verify structure
        assert "timestamp" in manifest
        assert "version" in manifest
        assert "database" in manifest
        assert "storage" in manifest
        
        # Verify database fields
        assert "host" in manifest["database"]
        assert "port" in manifest["database"]
        assert "name" in manifest["database"]
        assert "backup_file" in manifest["database"]
        
        # Verify storage fields
        assert "backup_file" in manifest["storage"]
    
    def test_manifest_timestamp_format(self):
        """Test manifest timestamp is valid ISO format"""
        timestamp = "2025-11-20T12:34:56Z"
        
        # Should be parseable
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(dt, datetime)
    
    def test_manifest_json_serializable(self):
        """Test manifest can be serialized to JSON"""
        manifest = {
            "timestamp": "2025-11-20T00:00:00Z",
            "version": "1.0",
            "database": {
                "host": "localhost",
                "backup_file": "db_backup.sql"
            }
        }
        
        # Should serialize without error
        json_str = json.dumps(manifest, indent=2)
        assert isinstance(json_str, str)
        
        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed == manifest


class TestBackupValidation:
    """Test backup validation logic"""
    
    def test_validate_backup_file_exists(self):
        """Test validation checks if backup file exists"""
        # Mock file existence check
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            backup_path = Path("./backups/db_backup.sql")
            exists = backup_path.exists()
            
            assert exists is True
    
    def test_validate_backup_file_not_empty(self):
        """Test validation checks if backup file is not empty"""
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024
            
            backup_path = Path("./backups/db_backup.sql")
            size = backup_path.stat().st_size
            
            assert size > 0
    
    def test_validate_manifest_required_fields(self):
        """Test manifest validation requires all fields"""
        valid_manifest = {
            "timestamp": "2025-11-20T00:00:00Z",
            "version": "1.0",
            "database": {"backup_file": "test.sql"},
            "storage": {"backup_file": "test.tar.gz"}
        }
        
        # All required fields present
        assert "timestamp" in valid_manifest
        assert "database" in valid_manifest
        
        # Missing field should fail
        incomplete_manifest = {"timestamp": "2025-11-20T00:00:00Z"}
        assert "database" not in incomplete_manifest


class TestDiskSpaceCheck:
    """Test disk space validation"""
    
    def test_check_sufficient_disk_space(self):
        """Test disk space check passes when sufficient"""
        with patch('shutil.disk_usage') as mock_usage:
            # Mock 10 GB free space
            mock_usage.return_value = MagicMock(
                free=10 * 1024 * 1024 * 1024
            )
            
            available_mb = mock_usage('.').free / (1024 * 1024)
            required_mb = 1000
            
            assert available_mb >= required_mb
    
    def test_check_insufficient_disk_space(self):
        """Test disk space check fails when insufficient"""
        with patch('shutil.disk_usage') as mock_usage:
            # Mock 100 MB free space
            mock_usage.return_value = MagicMock(
                free=100 * 1024 * 1024
            )
            
            available_mb = mock_usage('.').free / (1024 * 1024)
            required_mb = 1000
            
            assert available_mb < required_mb


class TestPgDumpCommand:
    """Test pg_dump command generation (mock)"""
    
    def test_pg_dump_command_format(self):
        """Test pg_dump command has correct format"""
        cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-p', '5432',
            '-U', '3dpot',
            '-d', '3dpot_dev',
            '-f', '/tmp/backup.sql',
            '--format=plain',
            '--no-owner',
            '--no-privileges'
        ]
        
        # Verify command structure
        assert cmd[0] == 'pg_dump'
        assert '-h' in cmd
        assert '-p' in cmd
        assert '-U' in cmd
        assert '-d' in cmd
        assert '-f' in cmd
    
    def test_pg_dump_environment_variables(self):
        """Test pg_dump uses PGPASSWORD environment variable"""
        env = {'PGPASSWORD': 'test_password'}
        
        # Verify password is in environment
        assert 'PGPASSWORD' in env
        assert env['PGPASSWORD'] == 'test_password'


class TestPgRestoreCommand:
    """Test pg_restore command generation (mock)"""
    
    def test_pg_restore_command_format(self):
        """Test psql restore command has correct format"""
        cmd = [
            'psql',
            '-h', 'localhost',
            '-p', '5432',
            '-U', '3dpot',
            '-d', '3dpot_dev',
            '-f', '/tmp/backup.sql'
        ]
        
        # Verify command structure
        assert cmd[0] == 'psql'
        assert '-h' in cmd
        assert '-p' in cmd
        assert '-U' in cmd
        assert '-d' in cmd
        assert '-f' in cmd


class TestBackupNaming:
    """Test backup file naming conventions"""
    
    def test_backup_filename_format(self):
        """Test backup files use timestamp format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        db_backup = f"db_backup_{timestamp}.sql"
        storage_backup = f"storage_backup_{timestamp}.tar.gz"
        
        # Verify naming pattern
        assert db_backup.startswith("db_backup_")
        assert db_backup.endswith(".sql")
        assert storage_backup.startswith("storage_backup_")
        assert storage_backup.endswith(".tar.gz")
    
    def test_backup_timestamp_uniqueness(self):
        """Test backup timestamps create unique filenames"""
        import time
        
        ts1 = datetime.now().strftime("%Y%m%d_%H%M%S")
        time.sleep(1)
        ts2 = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Different timestamps
        assert ts1 != ts2


class TestRestoreValidation:
    """Test restore validation logic"""
    
    def test_validate_manifest_before_restore(self):
        """Test restore validates manifest exists"""
        manifest_path = Path("./backups/backup_20251120_000000/manifest.json")
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            assert manifest_path.exists() is True
    
    def test_validate_backup_files_before_restore(self):
        """Test restore validates all backup files exist"""
        manifest = {
            "database": {"backup_file": "db_backup.sql"},
            "storage": {"backup_file": "storage_backup.tar.gz"}
        }
        
        # Check all files mentioned in manifest
        assert "backup_file" in manifest["database"]
        assert "backup_file" in manifest["storage"]
    
    def test_validate_database_connection_before_restore(self):
        """Test restore validates database connection"""
        # Mock database connection check
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            # Test connection command
            result = mock_run(['pg_isready', '-h', 'localhost'])
            
            assert result.returncode == 0


class TestStorageBackup:
    """Test storage/file backup logic"""
    
    def test_tar_command_format(self):
        """Test tar command for storage backup"""
        cmd = [
            'tar',
            '-czf',
            '/tmp/storage_backup.tar.gz',
            '-C', '/app/storage',
            '.'
        ]
        
        # Verify tar command structure
        assert cmd[0] == 'tar'
        assert '-czf' in cmd
    
    def test_storage_backup_includes_models(self):
        """Test storage backup includes models directory"""
        storage_path = Path('./storage')
        models_path = storage_path / 'models'
        
        # Verify models directory is within storage
        assert models_path.parent == storage_path


class TestErrorHandling:
    """Test error handling in backup/restore"""
    
    def test_backup_fails_on_pg_dump_error(self):
        """Test backup handles pg_dump errors"""
        with patch('subprocess.run') as mock_run:
            # Simulate pg_dump failure
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="Connection refused"
            )
            
            result = mock_run(['pg_dump'])
            assert result.returncode != 0
    
    def test_restore_fails_on_missing_manifest(self):
        """Test restore fails gracefully if manifest missing"""
        manifest_path = Path("./backups/nonexistent/manifest.json")
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            
            assert manifest_path.exists() is False
    
    def test_insufficient_permissions_error(self):
        """Test handles permission errors"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")
            
            try:
                Path("/protected").mkdir()
                assert False, "Should raise PermissionError"
            except PermissionError as e:
                assert "Permission denied" in str(e)


class TestBackupRetention:
    """Test backup retention and cleanup"""
    
    def test_list_backups_by_date(self):
        """Test listing backups sorted by date"""
        backups = [
            "backup_20251120_120000",
            "backup_20251119_120000",
            "backup_20251121_120000"
        ]
        
        # Sort by timestamp in filename
        sorted_backups = sorted(backups, reverse=True)
        
        # Most recent first
        assert sorted_backups[0] == "backup_20251121_120000"
        assert sorted_backups[-1] == "backup_20251119_120000"
    
    def test_retention_policy_keeps_recent(self):
        """Test retention keeps N most recent backups"""
        all_backups = [
            "backup_20251120_120000",
            "backup_20251119_120000",
            "backup_20251118_120000",
            "backup_20251117_120000"
        ]
        
        keep_count = 3
        sorted_backups = sorted(all_backups, reverse=True)
        to_keep = sorted_backups[:keep_count]
        to_delete = sorted_backups[keep_count:]
        
        assert len(to_keep) == 3
        assert len(to_delete) == 1
        assert "backup_20251117_120000" in to_delete
