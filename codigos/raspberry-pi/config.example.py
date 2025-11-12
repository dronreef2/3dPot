#!/usr/bin/env python3
"""
3dPot Quality Control Station - Configuration Template
Configuration file for Raspberry Pi QC system
Copy this file to 'config.py' and adjust values
"""

# =============================================================================
# CAMERA CONFIGURATION
# =============================================================================
CAMERA_CONFIG = {
    'width': 640,           # Image width in pixels
    'height': 480,          # Image height in pixels
    'fps': 30,              # Frames per second
    'format': 'RGB888',     # Image format
    'shutter_speed': 0,     # Auto exposure (0 = auto)
    'awb_mode': 'auto',     # Auto white balance mode
    'ae_mode': 'auto',      # Auto exposure mode
    'exposure': 0,          # Exposure compensation (-4 to +4)
}

# =============================================================================
# LED RING CONFIGURATION
# =============================================================================
LED_CONFIG = {
    'pin': 17,              # GPIO pin for LED control
    'pwm_frequency': 1000,  # PWM frequency in Hz
    'default_brightness': 80,  # Default brightness (0-100%)
    'min_brightness': 5,    # Minimum brightness to avoid dark images
    'max_brightness': 100,  # Maximum brightness
    'pulse_effect': True,   # Enable pulsing effect during inspection
    'pulse_duration': 2.0,  # Pulse duration in seconds
}

# =============================================================================
# MOTOR CONFIGURATION
# =============================================================================
MOTOR_CONFIG = {
    'step_pin': 18,         # GPIO pin for motor step
    'dir_pin': 19,          # GPIO pin for motor direction
    'enable_pin': 20,       # GPIO pin for motor enable (optional)
    'steps_per_revolution': 200,  # Steps per full revolution
    'microstep_factor': 1,      # Microstepping factor (1, 2, 4, 8, 16)
    'max_speed': 1000,          # Maximum speed (steps/second)
    'acceleration': 500,        # Acceleration (steps/second²)
    'home_direction': -1,       # Direction to home (-1 = CCW, 1 = CW)
    'homing_speed': 100,        # Speed for homing (steps/second)
    'step_delay': 0.001,        # Delay between steps in seconds
}

# =============================================================================
# INSPECTION CONFIGURATION
# =============================================================================
INSPECTION_CONFIG = {
    'positions_count': 8,           # Number of inspection positions
    'stabilization_delay': 0.5,     # Delay after movement (seconds)
    'capture_delay': 0.2,           # Delay before capture (seconds)
    'confidence_threshold': 0.7,    # Minimum confidence for approval (0-1)
    'defect_area_threshold': 100,   # Minimum area for defect detection (pixels)
    'save_images': True,            # Save inspection images to disk
    'images_path': '/tmp/inspections/',  # Path to save images
    'auto_analyze': True,           # Auto-analyze images during capture
    'max_inspection_time': 300,     # Maximum inspection time (seconds)
}

# =============================================================================
# DEFECT DETECTION CONFIGURATION
# =============================================================================
DETECTION_CONFIG = {
    'algorithm': 'template_matching',  # 'template_matching', 'edge_detection', 'color_analysis'
    'reference_image_path': '/static/models/reference.jpg',  # Path to reference image
    'blur_kernel_size': 5,         # Kernel size for Gaussian blur
    'threshold_low': 20,           # Lower threshold for edge detection
    'threshold_high': 50,          # Upper threshold for edge detection
    'min_contour_area': 50,        # Minimum contour area to consider
    'max_contours': 20,            # Maximum contours to analyze
    'defect_severity': {
        'critical_area': 1000,     # Area for critical defects
        'major_area': 500,         # Area for major defects
        'minor_area': 100          # Area for minor defects
    },
    'color_ranges': {              # Color analysis ranges (BGR format)
        'red': [(0, 0, 100), (100, 100, 255)],
        'green': [(0, 100, 0), (100, 255, 100)],
        'blue': [(100, 0, 0), (255, 100, 100)]
    }
}

# =============================================================================
# WEB INTERFACE CONFIGURATION
# =============================================================================
WEB_CONFIG = {
    'host': '0.0.0.0',            # Host to bind to
    'port': 5000,                 # Port to bind to
    'debug': False,               # Enable Flask debug mode
    'secret_key': '3dpot-qc-secret',  # Flask secret key
    'static_folder': 'static',    # Static files folder
    'template_folder': 'templates',   # Template files folder
    'max_content_length': 16 * 1024 * 1024,  # Max upload size (16MB)
    'cors_enabled': True,         # Enable CORS
    'api_timeout': 30,            # API timeout in seconds
}

# =============================================================================
# GPIO CONFIGURATION
# =============================================================================
GPIO_CONFIG = {
    'mode': 'BCM',                # GPIO mode ('BCM' or 'BOARD')
    'cleanup_on_exit': True,      # Cleanup GPIO on program exit
    'warning': False,             # Show GPIO warnings
    'pins': {
        'led_ring': 17,
        'motor_step': 18,
        'motor_direction': 19,
        'motor_enable': 20,
        'button_start': 21,       # Start inspection button
        'button_stop': 22,        # Stop inspection button
        'emergency_stop': 23,     # Emergency stop button
        'buzzer': 24,             # Buzzer for alerts
        'status_led_green': 25,   # Green status LED
        'status_led_red': 26,     # Red status LED
        'status_led_yellow': 27   # Yellow status LED
    }
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',              # Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': '/var/log/3dpot-qc.log',  # Log file path
    'max_file_size': 10 * 1024 * 1024,     # Max log file size (10MB)
    'backup_count': 5,            # Number of backup log files
    'console_output': True,       # Output logs to console
    'file_output': True,          # Output logs to file
    'sensor_logs': False,         # Log individual sensor readings
    'performance_logs': True,     # Log performance metrics
}

# =============================================================================
# PERFORMANCE CONFIGURATION
# =============================================================================
PERFORMANCE_CONFIG = {
    'enable_monitoring': True,    # Enable performance monitoring
    'monitor_interval': 5,        # Monitoring interval in seconds
    'memory_limit': 512,          # Memory usage limit in MB
    'cpu_limit': 80,              # CPU usage limit (percentage)
    'temperature_limit': 80,      # CPU temperature limit (°C)
    'disk_space_limit': 90,       # Disk usage limit (percentage)
    'log_performance': True,      # Log performance metrics
    'alert_on_limit': True,       # Alert when limits are exceeded
}

# =============================================================================
# SAFETY CONFIGURATION
# =============================================================================
SAFETY_CONFIG = {
    'max_runtime': 3600,          # Maximum runtime in seconds (1 hour)
    'emergency_timeout': 3,       # Emergency stop timeout in seconds
    'motor_overheat_protection': True,  # Enable motor protection
    'temperature_monitoring': True,     # Monitor system temperature
    'watchdog_timeout': 30,       # Watchdog timeout in seconds
    'auto_shutdown_on_error': False,    # Auto shutdown on critical errors
    'backup_power_detection': False,    # Detect backup power
    'sensor_validation': True,    # Validate sensor readings
}

# =============================================================================
# NETWORK CONFIGURATION
# =============================================================================
NETWORK_CONFIG = {
    'mqtt_enabled': True,         # Enable MQTT communication
    'mqtt_broker': 'localhost',   # MQTT broker address
    'mqtt_port': 1883,            # MQTT broker port
    'mqtt_username': '',          # MQTT username (empty if no auth)
    'mqtt_password': '',          # MQTT password
    'mqtt_topic_prefix': '3dpot/qc',  # MQTT topic prefix
    'webhook_enabled': False,     # Enable webhook notifications
    'webhook_url': '',            # Webhook URL for notifications
    'remote_access': False,       # Enable remote access
    'ssl_enabled': False,         # Enable SSL/HTTPS
    'certificate_path': '',       # Path to SSL certificate
    'private_key_path': '',       # Path to SSL private key
}

# =============================================================================
# DATA STORAGE CONFIGURATION
# =============================================================================
STORAGE_CONFIG = {
    'database_enabled': True,     # Enable database storage
    'database_path': '/var/lib/3dpot/qc.db',  # SQLite database path
    'backup_enabled': True,       # Enable automatic backups
    'backup_interval': 24,        # Backup interval in hours
    'backup_path': '/var/backups/3dpot/',  # Backup directory
    'retention_days': 30,         # Data retention in days
    'export_enabled': True,       # Enable data export
    'export_formats': ['json', 'csv'],  # Available export formats
    'cloud_sync': False,          # Sync to cloud storage
    'cloud_provider': '',         # Cloud storage provider
}

# =============================================================================
# CALIBRATION CONFIGURATION
# =============================================================================
CALIBRATION_CONFIG = {
    'auto_calibration': True,     # Enable automatic calibration
    'calibration_interval': 24,   # Calibration interval in hours
    'reference_images_path': '/static/references/',  # Path to reference images
    'calibration_tolerance': 0.05,    # Tolerance for calibration (0-1)
    'manual_calibration_required': False,  # Require manual calibration
    'calibration_validation': True,  # Validate calibration results
    'save_calibration_data': True,   # Save calibration data
    'calibration_backup': True,      # Backup calibration data
}

# =============================================================================
# UI/UX CONFIGURATION
# =============================================================================
UI_CONFIG = {
    'theme': 'dark',              # UI theme ('dark', 'light', 'auto')
    'language': 'pt-BR',          # Interface language
    'refresh_interval': 2,        # Auto-refresh interval in seconds
    'show_advanced_options': False,  # Show advanced options in UI
    'enable_keyboard_shortcuts': True,  # Enable keyboard shortcuts
    'auto_hide_sidebar': False,   # Auto-hide sidebar after inactivity
    'animations_enabled': True,   # Enable UI animations
    'compact_view': False,        # Use compact view
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_full_config():
    """Return complete configuration dictionary"""
    return {
        'camera': CAMERA_CONFIG,
        'led': LED_CONFIG,
        'motor': MOTOR_CONFIG,
        'inspection': INSPECTION_CONFIG,
        'detection': DETECTION_CONFIG,
        'web': WEB_CONFIG,
        'gpio': GPIO_CONFIG,
        'logging': LOGGING_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'safety': SAFETY_CONFIG,
        'network': NETWORK_CONFIG,
        'storage': STORAGE_CONFIG,
        'calibration': CALIBRATION_CONFIG,
        'ui': UI_CONFIG
    }

def load_config_from_file(config_path):
    """Load configuration from external file"""
    import json
    try:
        with open(config_path, 'r') as f:
            file_config = json.load(f)
        
        # Merge file configuration with defaults
        full_config = get_full_config()
        for section, values in file_config.items():
            if section in full_config:
                full_config[section].update(values)
        
        return full_config
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        return get_full_config()
    except json.JSONDecodeError as e:
        print(f"Error parsing configuration file: {e}")
        return get_full_config()

def validate_config(config):
    """Validate configuration values"""
    errors = []
    
    # Validate camera config
    if not (320 <= config['camera']['width'] <= 1920):
        errors.append("Camera width must be between 320 and 1920")
    
    if not (240 <= config['camera']['height'] <= 1080):
        errors.append("Camera height must be between 240 and 1080")
    
    # Validate inspection config
    if not (1 <= config['inspection']['positions_count'] <= 16):
        errors.append("Positions count must be between 1 and 16")
    
    if not (0 <= config['inspection']['confidence_threshold'] <= 1):
        errors.append("Confidence threshold must be between 0 and 1")
    
    # Validate GPIO pins
    used_pins = set(config['gpio']['pins'].values())
    if len(used_pins) != len(config['gpio']['pins'].values()):
        errors.append("GPIO pins must be unique")
    
    return errors

if __name__ == "__main__":
    # Print configuration summary
    config = get_full_config()
    print("3dPot QC Station Configuration")
    print("=" * 40)
    
    for section, values in config.items():
        print(f"\n{section.upper()}:")
        for key, value in values.items():
            print(f"  {key}: {value}")
    
    # Validate configuration
    errors = validate_config(config)
    if errors:
        print("\nVALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nConfiguration is valid!")