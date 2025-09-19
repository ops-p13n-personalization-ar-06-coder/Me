
import json
import configparser
import os
from typing import Any, Dict, List, Tuple, Union


class ConfigurationError(Exception):
    pass


class ConfigurationProcessor:
    def __init__(self, schema_definition: dict):
        self.schema = schema_definition
        self.configurations = []
    
    def load_config_file(self, filepath: str, file_format: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            if file_format == "json":
                config = json.loads(content)
            elif file_format == "ini":
                config = self._parse_ini(content)
            else:
                return False
            
            self.configurations.append(config)
            return True
        except:
            return False
    
    def _parse_ini(self, content: str) -> dict:
        parser = configparser.ConfigParser()
        parser.read_string(content)
        
        result = {}
        for section_name in parser.sections():
            section = {}
            for key, value in parser.items(section_name):
                section[key] = self._parse_ini_value(value)
            result[section_name] = section
        
        return result
    
    def _parse_ini_value(self, value: str) -> Any:
        value = value.strip()
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return value
    
    def merge_configurations(self) -> dict:
        if not self.configurations:
            return {}
        
        result = {}
        for config in self.configurations:
            result = self._deep_merge(result, config)
        
        return result
    
    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def validate_configuration(self, config: dict) -> Tuple[bool, List[str]]:
        errors = []
        self._validate_dict(config, self.schema, "", errors)
        return len(errors) == 0, errors
    
    def _validate_dict(self, data: dict, schema: dict, path: str, errors: List[str]):
        for field_name, field_schema in schema.items():
            current_path = f"{path}.{field_name}" if path else field_name
            
            if field_schema.get("required", False) and field_name not in data:
                errors.append(f"Required field '{current_path}' is missing")
                continue
            
            if field_name not in data:
                continue
            
            value = data[field_name]
            self._validate_field(value, field_schema, current_path, errors)
    
    def _validate_field(self, value: Any, schema: dict, path: str, errors: List[str]):
        expected_type = schema.get("type")
        
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"Field '{path}' must be string, got {type(value).__name__}")
            return
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"Field '{path}' must be integer, got {type(value).__name__}")
            return
        elif expected_type == "float" and not isinstance(value, (int, float)):
            errors.append(f"Field '{path}' must be float, got {type(value).__name__}")
            return
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Field '{path}' must be boolean, got {type(value).__name__}")
            return
        elif expected_type == "list" and not isinstance(value, list):
            errors.append(f"Field '{path}' must be list, got {type(value).__name__}")
            return
        elif expected_type == "dict" and not isinstance(value, dict):
            errors.append(f"Field '{path}' must be dict, got {type(value).__name__}")
            return
        
        if "min_value" in schema and isinstance(value, (int, float)):
            if value < schema["min_value"]:
                errors.append(f"Field '{path}' value {value} is below minimum {schema['min_value']}")
        
        if "max_value" in schema and isinstance(value, (int, float)):
            if value > schema["max_value"]:
                errors.append(f"Field '{path}' value {value} is above maximum {schema['max_value']}")
        
        if "min_length" in schema and isinstance(value, (str, list)):
            if len(value) < schema["min_length"]:
                errors.append(f"Field '{path}' length {len(value)} is below minimum {schema['min_length']}")
        
        if "max_length" in schema and isinstance(value, (str, list)):
            if len(value) > schema["max_length"]:
                errors.append(f"Field '{path}' length {len(value)} is above maximum {schema['max_length']}")
        
        if "allowed_values" in schema:
            if value not in schema["allowed_values"]:
                errors.append(f"Field '{path}' value '{value}' not in allowed values {schema['allowed_values']}")
        
        if expected_type == "dict" and "nested_schema" in schema and isinstance(value, dict):
            self._validate_dict(value, schema["nested_schema"], path, errors)
    
    def transform_values(self, config: dict) -> dict:
        result = {}
        self._transform_dict(config, self.schema, result)
        return result
    
    def _transform_dict(self, data: dict, schema: dict, result: dict):
        for field_name, field_schema in schema.items():
            if field_name in data:
                value = data[field_name]
                result[field_name] = self._transform_field(value, field_schema)
            elif "default" in field_schema:
                result[field_name] = field_schema["default"]
        
        for field_name, value in data.items():
            if field_name not in schema:
                result[field_name] = value
    
    def _transform_field(self, value: Any, schema: dict) -> Any:
        expected_type = schema.get("type")
        
        if expected_type == "integer":
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
        elif expected_type == "float":
            try:
                value = float(value)
            except (ValueError, TypeError):
                pass
        elif expected_type == "boolean":
            if isinstance(value, str):
                value = value.lower() in ('true', '1', 'yes', 'on')
        elif expected_type == "string":
            if not isinstance(value, str):
                value = str(value)
        
        if "transform" in schema and isinstance(value, str):
            transform = schema["transform"]
            if transform == "uppercase":
                value = value.upper()
            elif transform == "lowercase":
                value = value.lower()
            elif transform == "strip":
                value = value.strip()
        elif "transform" in schema and isinstance(value, (int, float)):
            transform = schema["transform"]
            if transform == "abs":
                value = abs(value)
        
        if expected_type == "dict" and "nested_schema" in schema and isinstance(value, dict):
            nested_result = {}
            self._transform_dict(value, schema["nested_schema"], nested_result)
            value = nested_result
        
        return value
    
    def process_all(self) -> dict:
        merged = self.merge_configurations()
        transformed = self.transform_values(merged)
        is_valid, errors = self.validate_configuration(transformed)
        
        if not is_valid:
            error_message = "Configuration validation failed: " + "; ".join(errors)
            raise ConfigurationError(error_message)
        
        return transformed
