"""Configuration management."""

import os
from pathlib import Path
from typing import Optional, Any
import yaml


class Config:
    """Configuration manager for MaFin Terminal."""

    DEFAULT_CONFIG = {
        'display': {
            'fullscreen': True,
            'theme': 'dark',
            'color_scheme': 'bloomberg_orange',
            'font_size': 14
        },
        'multi_monitor': {
            'use_all_monitors': True,
            'primary_monitor_only': False
        },
        'data_providers': {
            'yahoo_finance': {
                'enabled': True
            },
            'alpha_vantage': {
                'enabled': False,
                'api_key': ''
            }
        },
        'portfolio': {
            'default_currency': 'USD',
            'display_currency': 'USD'
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/mafin.log'
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self._config = self.DEFAULT_CONFIG.copy()
        self._config_path = config_path or self._get_default_config_path()
        self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default config path."""
        return os.path.join(os.getcwd(), 'config.yaml')

    def _load_config(self):
        """Load configuration from file."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(self._config, user_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def _merge_config(self, base: dict, update: dict):
        """Recursively merge configuration."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self):
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
        with open(self._config_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get_all(self) -> dict:
        """Get all configuration."""
        return self._config.copy()


_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
