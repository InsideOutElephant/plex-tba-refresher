# plex_refresher/utils/config_loader.py
import yaml
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse
from plex_refresher.exceptions.config_errors import ConfigurationError  # Fixed import
from plex_refresher.config.config_schema import CONFIG_SCHEMA          # Fixed import
import logging

class ConfigLoader:
    @staticmethod
    def validate_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_token(token: str) -> bool:
        return bool(token and len(token) >= 20)

    @classmethod
    def validate_config_field(cls, field_name: str, field_value: Any, rules: Dict) -> Any:
        if not isinstance(field_value, rules['type']):
            raise ConfigurationError(
                f"Invalid type for {field_name}. Expected {rules['type'].__name__}, got {type(field_value).__name__}"
            )

        if isinstance(field_value, (int, float)) and 'min' in rules:
            if field_value < rules['min']:
                raise ConfigurationError(
                    f"{field_name} must be at least {rules['min']}"
                )

        if isinstance(field_value, (int, float)) and 'max' in rules:
            if field_value > rules['max']:
                raise ConfigurationError(
                    f"{field_name} must be no more than {rules['max']}"
                )

        if 'values' in rules and field_value not in rules['values']:
            raise ConfigurationError(
                f"Invalid value for {field_name}. Must be one of: {', '.join(rules['values'])}"
            )

        return field_value

    @classmethod
    def validate_config_section(cls, section_name: str, section_data: Dict, schema: Dict) -> Dict:
        validated = {}
        
        for field_name, rules in schema['fields'].items():
            if field_name not in section_data:
                if rules.get('required', False):
                    raise ConfigurationError(f"Missing required field: {section_name}.{field_name}")
                if 'default' in rules:
                    validated[field_name] = rules['default']
                continue
                
            validated[field_name] = cls.validate_config_field(
                f"{section_name}.{field_name}",
                section_data[field_name],
                rules
            )
            
        unknown_fields = set(section_data.keys()) - set(schema['fields'].keys())
        if unknown_fields:
            logging.warning(f"Unknown fields in {section_name} configuration: {', '.join(unknown_fields)}")
            
        return validated

    @classmethod
    def load_and_validate(cls, config_path: Path = Path('/app/data/config.yaml')) -> Dict:
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            if not isinstance(config, dict):
                raise ConfigurationError("Configuration must be a YAML dictionary")
                
            validated_config = {}
            for section_name, schema in CONFIG_SCHEMA.items():
                if section_name not in config:
                    if schema['required']:
                        raise ConfigurationError(f"Missing required section: {section_name}")
                    continue
                    
                validated_config[section_name] = cls.validate_config_section(
                    section_name,
                    config[section_name],
                    schema
                )
            
            if not cls.validate_url(validated_config['plex']['url']):
                raise ConfigurationError("Invalid Plex URL format")
                
            if not cls.validate_token(validated_config['plex']['token']):
                raise ConfigurationError("Invalid Plex token format")
                
            if not validated_config['plex'].get('libraries'):
                validated_config['plex'].pop('libraries', None)
            
            return validated_config
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse config file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Configuration error: {str(e)}")

