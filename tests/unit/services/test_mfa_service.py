"""
Unit tests for MFA Service
Testing TOTP generation, QR codes, backup codes, and validation
Sprint 9
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import pyotp
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.services.mfa_service import (
    MFAService,
    MFAError,
    MFANotEnabledException,
    MFAInvalidCodeException
)


@pytest.fixture
def mfa_service():
    """Create MFA service instance"""
    return MFAService()


@pytest.fixture
def mock_user():
    """Create mock user"""
    user = Mock()
    user.id = "test-user-id"
    user.username = "testuser"
    user.email = "test@example.com"
    user.mfa_enabled = False
    user.mfa_secret = None
    user.mfa_backup_codes = []
    user.is_superuser = False
    user.role = "user"
    return user


@pytest.fixture
def mock_db():
    """Create mock database session"""
    db = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


class TestSecretGeneration:
    """Test TOTP secret generation"""
    
    def test_generate_secret(self, mfa_service):
        """Test that generate_secret returns valid base32 string"""
        secret = mfa_service.generate_secret()
        
        # Should be valid base32
        assert isinstance(secret, str)
        assert len(secret) == 32  # pyotp default length
        
        # Should be uppercase alphanumeric (base32)
        assert secret.isalnum()
        assert secret.isupper()
    
    def test_generate_secret_uniqueness(self, mfa_service):
        """Test that multiple calls generate different secrets"""
        secret1 = mfa_service.generate_secret()
        secret2 = mfa_service.generate_secret()
        
        assert secret1 != secret2


class TestTOTPUri:
    """Test TOTP URI generation for QR codes"""
    
    def test_get_totp_uri(self, mfa_service, mock_user):
        """Test TOTP URI generation"""
        secret = "JBSWY3DPEHPK3PXP"  # Example base32 secret
        
        uri = mfa_service.get_totp_uri(mock_user, secret)
        
        # Should be valid otpauth URI
        assert uri.startswith("otpauth://totp/")
        assert mock_user.email in uri
        assert "3dPot" in uri  # issuer name
        assert secret in uri
    
    def test_get_totp_uri_format(self, mfa_service, mock_user):
        """Test TOTP URI has correct format"""
        secret = "JBSWY3DPEHPK3PXP"
        uri = mfa_service.get_totp_uri(mock_user, secret)
        
        # Should contain key components
        assert "otpauth://totp/" in uri
        assert f"secret={secret}" in uri
        assert "issuer=" in uri


class TestQRCodeGeneration:
    """Test QR code image generation"""
    
    def test_generate_qr_code(self, mfa_service):
        """Test QR code generation returns base64 data URI"""
        uri = "otpauth://totp/test@example.com?secret=JBSWY3DPEHPK3PXP&issuer=3dPot"
        
        qr_code = mfa_service.generate_qr_code(uri)
        
        # Should be data URI with base64 PNG
        assert qr_code.startswith("data:image/png;base64,")
        assert len(qr_code) > 100  # Should have substantial content


class TestTOTPVerification:
    """Test TOTP code verification"""
    
    def test_verify_valid_totp_code(self, mfa_service):
        """Test verification of valid TOTP code"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        result = mfa_service.verify_totp_code(secret, code)
        assert result is True
    
    def test_verify_invalid_totp_code(self, mfa_service):
        """Test rejection of invalid TOTP code"""
        secret = pyotp.random_base32()
        
        result = mfa_service.verify_totp_code(secret, "000000")
        assert result is False
    
    def test_verify_totp_code_with_window(self, mfa_service):
        """Test TOTP verification accepts codes within time window"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Current code should always work
        current_code = totp.now()
        assert mfa_service.verify_totp_code(secret, current_code, window=1) is True


class TestMFAEnablement:
    """Test MFA enable flow"""
    
    def test_enable_mfa(self, mfa_service, mock_user, mock_db):
        """Test MFA enablement returns secret and QR code"""
        secret, qr_code = mfa_service.enable_mfa(mock_user, mock_db)
        
        # Should generate secret
        assert isinstance(secret, str)
        assert len(secret) == 32
        
        # Should generate QR code
        assert qr_code.startswith("data:image/png;base64,")
        
        # Should update user
        assert mock_user.mfa_secret == secret
        assert mock_user.mfa_enabled is False  # Not enabled until confirmed
        
        # Should commit to DB
        mock_db.commit.assert_called_once()
    
    def test_enable_mfa_generates_unique_secret(self, mfa_service, mock_db):
        """Test that each user gets unique secret"""
        user1 = Mock(id="user1", email="user1@example.com", mfa_enabled=False)
        user2 = Mock(id="user2", email="user2@example.com", mfa_enabled=False)
        
        secret1, _ = mfa_service.enable_mfa(user1, mock_db)
        secret2, _ = mfa_service.enable_mfa(user2, mock_db)
        
        assert secret1 != secret2


class TestMFAConfirmation:
    """Test MFA enrollment confirmation"""
    
    def test_confirm_mfa_with_valid_code(self, mfa_service, mock_user, mock_db):
        """Test MFA confirmation with valid code"""
        # Setup: user has secret but MFA not yet enabled
        secret = pyotp.random_base32()
        mock_user.mfa_secret = secret
        mock_user.mfa_enabled = False
        
        # Generate valid code
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        # Confirm
        result = mfa_service.confirm_mfa_enrollment(mock_user, code, mock_db)
        
        assert result is True
        assert mock_user.mfa_enabled is True
        mock_db.commit.assert_called_once()
    
    def test_confirm_mfa_with_invalid_code(self, mfa_service, mock_user, mock_db):
        """Test MFA confirmation fails with invalid code"""
        secret = pyotp.random_base32()
        mock_user.mfa_secret = secret
        mock_user.mfa_enabled = False
        
        # Invalid code
        with pytest.raises(MFAInvalidCodeException):
            mfa_service.confirm_mfa_enrollment(mock_user, "000000", mock_db)
        
        assert mock_user.mfa_enabled is False
    
    def test_confirm_mfa_without_secret(self, mfa_service, mock_user, mock_db):
        """Test confirmation fails if setup not initiated"""
        mock_user.mfa_secret = None
        
        with pytest.raises(MFAError, match="MFA setup não iniciado"):
            mfa_service.confirm_mfa_enrollment(mock_user, "123456", mock_db)


class TestMFADisablement:
    """Test MFA disable flow"""
    
    def test_disable_mfa(self, mfa_service, mock_user, mock_db):
        """Test MFA disablement clears secret and flag"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = "SOMESECRET"
        
        result = mfa_service.disable_mfa(mock_user, mock_db)
        
        assert result is True
        assert mock_user.mfa_enabled is False
        assert mock_user.mfa_secret is None
        mock_db.commit.assert_called_once()


class TestMFAValidation:
    """Test MFA code validation during login"""
    
    def test_validate_totp_code(self, mfa_service, mock_user):
        """Test validation of valid TOTP code"""
        secret = pyotp.random_base32()
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = secret
        
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        result = mfa_service.validate_mfa_code(mock_user, code)
        assert result is True
    
    def test_validate_invalid_code(self, mfa_service, mock_user):
        """Test validation rejects invalid code"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = pyotp.random_base32()
        
        with pytest.raises(MFAInvalidCodeException):
            mfa_service.validate_mfa_code(mock_user, "000000")
    
    def test_validate_when_mfa_not_enabled(self, mfa_service, mock_user):
        """Test validation fails when MFA not enabled"""
        mock_user.mfa_enabled = False
        
        with pytest.raises(MFANotEnabledException):
            mfa_service.validate_mfa_code(mock_user, "123456")
    
    def test_validate_backup_code(self, mfa_service, mock_user):
        """Test validation accepts valid backup code"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = pyotp.random_base32()
        mock_user.mfa_backup_codes = ["1234-5678", "9999-0000"]
        
        result = mfa_service.validate_mfa_code(mock_user, "1234-5678")
        assert result is True
        
        # Backup code should be removed after use
        assert "1234-5678" not in mock_user.mfa_backup_codes
        assert len(mock_user.mfa_backup_codes) == 1
    
    def test_validate_backup_code_case_insensitive(self, mfa_service, mock_user):
        """Test backup code validation is case-insensitive"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = pyotp.random_base32()
        mock_user.mfa_backup_codes = ["AbCd-1234"]
        
        result = mfa_service.validate_mfa_code(mock_user, "abcd-1234")
        assert result is True
    
    def test_validate_backup_code_with_spaces(self, mfa_service, mock_user):
        """Test backup code validation ignores spaces"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = pyotp.random_base32()
        mock_user.mfa_backup_codes = ["1234-5678"]
        
        result = mfa_service.validate_mfa_code(mock_user, " 1234-5678 ")
        assert result is True
    
    def test_validate_used_backup_code_fails(self, mfa_service, mock_user):
        """Test backup code can only be used once"""
        mock_user.mfa_enabled = True
        mock_user.mfa_secret = pyotp.random_base32()
        mock_user.mfa_backup_codes = ["1234-5678"]
        
        # First use succeeds
        result = mfa_service.validate_mfa_code(mock_user, "1234-5678")
        assert result is True
        
        # Second use fails (code removed)
        with pytest.raises(MFAInvalidCodeException):
            mfa_service.validate_mfa_code(mock_user, "1234-5678")


class TestBackupCodes:
    """Test backup code generation"""
    
    def test_generate_backup_codes(self, mfa_service):
        """Test backup code generation"""
        codes = mfa_service.generate_backup_codes(count=10)
        
        assert len(codes) == 10
        
        # Each code should be in XXXX-XXXX format
        for code in codes:
            parts = code.split("-")
            assert len(parts) == 2
            assert len(parts[0]) == 4
            assert len(parts[1]) == 4
            assert parts[0].isdigit()
            assert parts[1].isdigit()
    
    def test_generate_backup_codes_uniqueness(self, mfa_service):
        """Test backup codes are unique"""
        codes = mfa_service.generate_backup_codes(count=20)
        
        # All codes should be unique
        assert len(codes) == len(set(codes))
    
    def test_generate_custom_count(self, mfa_service):
        """Test generating custom number of backup codes"""
        codes = mfa_service.generate_backup_codes(count=5)
        assert len(codes) == 5


class TestMFARequirement:
    """Test MFA requirement logic"""
    
    def test_mfa_not_required_for_regular_user(self, mfa_service, mock_user):
        """Test MFA is not required for regular users by default"""
        mock_user.is_superuser = False
        mock_user.role = "user"
        
        with patch('backend.core.config.MFA_REQUIRED_FOR_ADMIN', False):
            required = mfa_service.is_mfa_required(mock_user)
            assert required is False
    
    def test_mfa_required_for_admin_when_configured(self, mfa_service, mock_user):
        """Test MFA is required for admins when MFA_REQUIRED_FOR_ADMIN=true"""
        mock_user.is_superuser = True
        mock_user.role = "admin"
        
        with patch('backend.core.config.MFA_REQUIRED_FOR_ADMIN', True):
            required = mfa_service.is_mfa_required(mock_user)
            assert required is True
    
    def test_mfa_not_required_for_admin_when_not_configured(self, mfa_service, mock_user):
        """Test MFA is optional for admins when MFA_REQUIRED_FOR_ADMIN=false"""
        mock_user.is_superuser = True
        mock_user.role = "admin"
        
        with patch('backend.core.config.MFA_REQUIRED_FOR_ADMIN', False):
            required = mfa_service.is_mfa_required(mock_user)
            assert required is False
