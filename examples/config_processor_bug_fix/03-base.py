
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
                return int(value)
            except ValueError:
                return value
    
    def merge_configurations(self) -> dict:
        if not self.configurations:
            return {}
        
        result = self.configurations[0]
        for config in self.configurations[1:]:
            result = self._shallow_merge(result, config)
        
        return result
    
    def _shallow_merge(self, base: dict, overlay: dict) -> dict:
        result = base.copy()
        result.update(overlay)
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
            errors.append(f"Field '{path}' must be string")
            return
        elif expected_type == "integer" and not isinstance(value, int):
            errors.append(f"Field '{path}' must be integer")
            return
        elif expected_type == "boolean" and not isinstance(value, bool):
            errors.append(f"Field '{path}' must be boolean")
            return
        elif expected_type == "dict" and not isinstance(value, dict):
            errors.append(f"Field '{path}' must be dict")
            return
        
        if "min_value" in schema and isinstance(value, (int, float)):
            if value <= schema["min_value"]:
                errors.append(f"Field '{path}' value {value} is below minimum {schema['min_value']}")
        
        if "allowed_values" in schema:
            if value not in schema["allowed_values"]:
                errors.append(f"Field '{path}' invalid value")
        
        if expected_type == "dict" and "nested_schema" in schema and isinstance(value, dict):
            self._validate_dict(value, schema["nested_schema"], path, errors)
    
    def transform_values(self, config: dict) -> dict:
        result = config.copy()
        self._transform_dict(result, self.schema)
        return result
    
    def _transform_dict(self, data: dict, schema: dict):
        for field_name, field_schema in schema.items():
            if "default" in field_schema and field_name not in data:
                data[field_name] = field_schema["default"]
            
            if field_name in data:
                value = data[field_name]
                if "transform" in field_schema and isinstance(value, str):
                    transform = field_schema["transform"]
                    if transform == "uppercase":
                        data[field_name] = value.upper()
    
    def process_all(self) -> dict:
        merged = self.merge_configurations()
        is_valid, errors = self.validate_configuration(merged)
        
        if not is_valid:
            error_message = "Validation failed: " + "; ".join(errors)
            raise ConfigurationError(error_message)
        
        return self.transform_values(merged)
