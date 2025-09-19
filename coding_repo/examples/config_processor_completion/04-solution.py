import json
import configparser
import os
from typing import Any, Dict, List, Tuple


class ConfigurationError(Exception):
    pass


class ConfigurationProcessor:
    def __init__(self, schema_definition: dict):
        self.schema = schema_definition
        self.configurations: List[dict] = []

    # ---------------- File Loading ----------------

    def load_config_file(self, filepath: str, file_format: str) -> bool:
        try:
            if not os.path.exists(filepath):
                return False
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if file_format == "json":
                config = json.loads(content)
                if not isinstance(config, dict):
                    return False
            elif file_format == "ini":
                config = self._parse_ini(content)
            else:
                return False
            self.configurations.append(config)
            return True
        except Exception:
            return False

    def _parse_ini(self, content: str) -> dict:
        parser = configparser.ConfigParser()
        parser.read_string(content)
        result: Dict[str, dict] = {}
        for section_name in parser.sections():
            section: Dict[str, Any] = {}
            for key, value in parser.items(section_name):
                section[key] = self._parse_ini_value(value)
            result[section_name] = section
        return result

    def _parse_ini_value(self, value: str) -> Any:
        v = value.strip()
        low = v.lower()
        if low in {"true", "yes", "on", "1"}:
            return True
        if low in {"false", "no", "off", "0"}:
            return False
        try:
            if any(ch in v for ch in ".eE"):
                return float(v)
            return int(v)
        except ValueError:
            return v

    # ---------------- Merging ----------------

    def merge_configurations(self) -> dict:
        if not self.configurations:
            return {}
        merged: Dict[str, Any] = {}
        for cfg in self.configurations:
            merged = self._deep_merge(merged, cfg)
        return merged

    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        out = dict(base)
        for k, v in overlay.items():
            if k in out and isinstance(out[k], dict) and isinstance(v, dict):
                out[k] = self._deep_merge(out[k], v)
            else:
                out[k] = v
        return out

    # ---------------- Validation ----------------

    def validate_configuration(self, config: dict) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        self._validate_dict(config, self.schema, path="", errors=errors)
        return (len(errors) == 0, errors)

    def _validate_dict(self, data: dict, schema: dict, path: str, errors: List[str]):
        for field, rule in schema.items():
            full = f"{path}.{field}" if path else field
            # required
            if rule.get("required") and field not in data:
                errors.append(f"Required field '{full}' is missing")
                continue
            if field not in data:
                continue
            value = data[field]
            self._validate_field(value, rule, full, errors)

    def _validate_field(self, value: Any, rule: dict, full: str, errors: List[str]):
        typ = rule.get("type")
        # type checking
        if typ == "string" and not isinstance(value, str):
            errors.append(f"Field '{full}' must be string, got {type(value).__name__}")
            return
        if typ == "integer" and not isinstance(value, int):
            errors.append(f"Field '{full}' must be integer, got {type(value).__name__}")
            return
        if typ == "float" and not isinstance(value, (int, float)):
            errors.append(f"Field '{full}' must be float, got {type(value).__name__}")
            return
        if typ == "boolean" and not isinstance(value, bool):
            errors.append(f"Field '{full}' must be boolean, got {type(value).__name__}")
            return
        if typ == "list" and not isinstance(value, list):
            errors.append(f"Field '{full}' must be list, got {type(value).__name__}")
            return
        if typ == "dict" and not isinstance(value, dict):
            errors.append(f"Field '{full}' must be dict, got {type(value).__name__}")
            return

        # numeric ranges
        if isinstance(value, (int, float)):
            if "min_value" in rule and value < rule["min_value"]:
                errors.append(f"Field '{full}' value {value} is below minimum {rule['min_value']}")
            if "max_value" in rule and value > rule["max_value"]:
                errors.append(f"Field '{full}' value {value} is above maximum {rule['max_value']}")

        # length constraints
        if isinstance(value, (str, list)):
            if "min_length" in rule and len(value) < rule["min_length"]:
                errors.append(f"Field '{full}' length {len(value)} is below minimum {rule['min_length']}")
            if "max_length" in rule and len(value) > rule["max_length"]:
                errors.append(f"Field '{full}' length {len(value)} is above maximum {rule['max_length']}")

        # allowed values
        if "allowed_values" in rule:
            if value not in rule["allowed_values"]:
                errors.append(f"Field '{full}' value '{value}' not in allowed values {rule['allowed_values']}")

        # nested
        if typ == "dict" and isinstance(value, dict) and "nested_schema" in rule:
            self._validate_dict(value, rule["nested_schema"], full, errors)

    # ---------------- Transform ----------------

    def transform_values(self, config: dict) -> dict:
        out: Dict[str, Any] = {}
        self._transform_dict(config, self.schema, out)
        return out

    def _transform_dict(self, data: dict, schema: dict, out: dict):
        # apply schema-defined fields
        for field, rule in schema.items():
            if field in data:
                out[field] = self._transform_field(data[field], rule)
            elif "default" in rule:
                out[field] = rule["default"]
        # pass-through extra fields
        for field, value in data.items():
            if field not in schema:
                out[field] = value

    def _transform_field(self, value: Any, rule: dict) -> Any:
        typ = rule.get("type")

        def to_bool(s: str) -> bool:
            return s.strip().lower() in {"true", "1", "yes", "on"}

        # type coercion
        if typ == "integer":
            try:
                if isinstance(value, str) and value.strip():
                    return int(value.strip())
            except Exception:
                pass
        elif typ == "float":
            try:
                if isinstance(value, str) and value.strip():
                    return float(value.strip())
            except Exception:
                pass
        elif typ == "boolean":
            if isinstance(value, str):
                return to_bool(value)
        elif typ == "string":
            if not isinstance(value, str):
                value = str(value)

        # nested dicts
        if typ == "dict" and isinstance(value, dict) and "nested_schema" in rule:
            nested: Dict[str, Any] = {}
            self._transform_dict(value, rule["nested_schema"], nested)
            value = nested

        # transforms
        transform = rule.get("transform")
        if transform:
            if isinstance(value, str):
                if transform == "uppercase":
                    value = value.upper()
                elif transform == "lowercase":
                    value = value.lower()
                elif transform == "strip":
                    value = value.strip()
            elif isinstance(value, (int, float)) and transform == "abs":
                value = abs(value)

        return value

    # ---------------- Pipeline ----------------

    def process_all(self) -> dict:
        merged = self.merge_configurations()
        transformed = self.transform_values(merged)
        ok, errors = self.validate_configuration(transformed)
        if not ok:
            raise ConfigurationError("Configuration validation failed: " + "; ".join(errors))
        return transformed
