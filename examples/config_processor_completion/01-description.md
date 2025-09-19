# Configuration Processor — Completion

Implement a configuration file processing system (`ConfigurationProcessor`) that merges multiple configuration files (JSON and INI), validates them against a schema, and applies value transformations.

Your task is to **implement the class from scratch** to satisfy the tests.

## Class and API

- Class Name: `ConfigurationProcessor`
- Constructor: `def __init__(self, schema_definition: dict)`
- Methods:
  - `load_config_file(self, filepath: str, file_format: str) -> bool`
  - `merge_configurations(self) -> dict`
  - `validate_configuration(self, config: dict) -> tuple[bool, list[str]]`
  - `transform_values(self, config: dict) -> dict`
  - `process_all(self) -> dict`

## Required Behavior

- **File Loading:**  
  Loads JSON or INI files. Returns `True` if successful, `False` otherwise. Handles file not found and parsing errors gracefully.

- **Merging:**  
  Later files override earlier ones with **deep merging** for nested dictionaries. Lists are replaced, not concatenated.

- **Validation:**  
  Checks types, required fields, min/max values, length constraints, allowed values, and nested schemas.

- **Transformation:**  
  Applies type coercion, default values, and transforms: `"uppercase"`, `"lowercase"`, `"strip"` for strings, `"abs"` for numbers.  
  Coerce:
  - `"123"` → `123`, `"-45"` → `-45`
  - `"15.5"` → `15.5`
  - `"true" | "1" | "yes" | "on"` (case-insensitive) → `True`, anything else → `False`
  - Any non-string to string if `type` is `"string"`
  - On failed conversion: leave the value unchanged

- **Error Handling:**  
  - File loading errors return `False`.  
  - `process_all()` must raise `ConfigurationError` with:  
    `"Configuration validation failed: {error1}; {error2}"`

## Schema Definition Format

Field properties:
- `type`: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"list"`, `"dict"`
- `required`: `True` if field must be present
- `default`: default value
- `min_value`, `max_value`: numeric range (int/float)
- `min_length`, `max_length`: len() for strings/lists
- `allowed_values`: allowed set
- `transform`: `"uppercase"`, `"lowercase"`, `"strip"`, `"abs"`
- `nested_schema`: dict schema for nested dicts

## Validation Error Message Formats (exact)

- Missing: `Required field '{full_path}' is missing`
- Type error: `Field '{full_path}' must be {expected_type}, got {actual_type_name}`  
  (expected_type is one of: string, integer, float, boolean, list, dict)
- Min value: `Field '{full_path}' value {value} is below minimum {min_value}`
- Max value: `Field '{full_path}' value {value} is above maximum {max_value}`
- Min length: `Field '{full_path}' length {length} is below minimum {min_length}`
- Max length: `Field '{full_path}' length {length} is above maximum {max_length}`
- Allowed: `Field '{full_path}' value '{value}' not in allowed values {allowed_values}`

Notes:
- Nested paths use dots (`database.host`, `app.database.host`).
- Type names in error messages are lowercase Python type names: `str`, `int`, `float`, `bool`, `list`, `dict`.

## Example Schema

```python
schema = {
    "database": {
        "type": "dict",
        "required": True,
        "nested_schema": {
            "host": {"type": "string", "required": True},
            "port": {"type": "integer", "min_value": 1, "max_value": 65535, "default": 5432},
            "username": {"type": "string", "min_length": 3, "max_length": 20}
        }
    },
    "debug": {"type": "boolean", "default": False},
    "log_level": {
        "type": "string",
        "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR"],
        "transform": "uppercase",
        "default": "INFO"
    },
    "timeout": {"type": "float", "min_value": 0.1, "max_value": 30.0},
    "features": {"type": "list", "min_length": 1},
    "name": {"type": "string", "transform": "strip"}
}
```
