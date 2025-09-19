# Configuration Processor — Bug Fix

You are given a buggy implementation of a configuration file processing system (`ConfigurationProcessor`) that is supposed to merge multiple configuration files (JSON and INI), validate them against a schema, and apply value transformations. However, the current implementation has several critical bugs.

Fix the provided `ConfigurationProcessor` class so that it meets the following requirements:

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

- **File Loading:** Loads JSON or INI files. Returns `True` if successful, `False` otherwise. Handles file not found and parsing errors gracefully.  

- **Merging:** Later files override earlier ones with deep merging for nested dictionaries.  

- **Validation:** Checks types, required fields, min/max values, length constraints, allowed values, and nested schemas.  

- **Transformation:** Applies type coercion, default values, and string/numeric transforms (uppercase, lowercase, strip, abs). Type coercion should handle standard string representations: convert string numbers to integers/floats (e.g., `"123"` -> `123`, `"15.5"` -> `15.5`) and string booleans to boolean values (e.g., `"true"`, `"false"`, `"1"`, `"0"`, case-insensitive).  

- **Error Handling:**  
  - File loading errors return `False`.  
  - Validation errors in `process_all()` must raise `ConfigurationError` with the format:  
    `"Configuration validation failed: {error1}; {error2}"`  

## Schema Definition Format

The schema supports the following field properties:

- `type`: `"string"`, `"integer"`, `"float"`, `"boolean"`, `"list"`, `"dict"`
- `required`: `True` if field must be present
- `default`: Default value if field is missing
- `min_value`, `max_value`: Numeric range validation for integers/floats
- `min_length`, `max_length`: Length validation for strings and lists
- `allowed_values`: List of allowed values for the field
- `transform`: String transformation: `"uppercase"`, `"lowercase"`, `"strip"`, or `"abs"` (for numbers)
- `nested_schema`: For dict types, defines validation schema for nested fields

## Type Coercion Rules

The `transform_values` method must handle automatic type conversion for the following cases:

- String to Integer: `"123"` -> `123`, `"-45"` -> `-45`
- String to Float: `"15.5"` -> `15.5`, `"3.14159"` -> `3.14159`
- String to Boolean: `"true"`, `"1"`, `"yes"`, `"on"` -> `True` (case-insensitive); other strings -> `False`
- Any type to String: Convert any non-string value to its string representation
- Failed conversions: If conversion fails, leave the original value unchanged

## Validation Error Message Formats

The `validate_configuration` method must produce detailed error messages with these exact formats:

- Missing required field: `"Required field '{full_path}' is missing"`
- Type error: `"Field '{full_path}' must be {expected_type}, got {actual_type_name}"`
  - Examples: `"Field 'debug' must be boolean, got str"`, `"Field 'count' must be integer, got str"`
- Minimum value error: `"Field '{full_path}' value {value} is below minimum {min_value}"`
- Maximum value error: `"Field '{full_path}' value {value} is above maximum {max_value}"`
- Minimum length error: `"Field '{full_path}' length {length} is below minimum {min_length}"`
- Maximum length error: `"Field '{full_path}' length {length} is above maximum {max_length}"`
- Allowed values error: `"Field '{full_path}' value '{value}' not in allowed values {allowed_values}"`

**Important Notes:**
- For nested fields, use dot notation in the path (e.g., `'database.host'`, `'app.database.host'`)
- Type names should be lowercase (e.g., `str`, `int`, `float`, `bool`, `list`, `dict`)
- The `allowed_values` should show the actual list format as returned by Python

## Example Schema and Usage

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

processor = ConfigurationProcessor(schema)
processor.load_config_file("base.json", "json")    
processor.load_config_file("override.ini", "ini")    
config = processor.process_all()
```

### Configuration File Format Examples

**JSON**
```json
{
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "debug": true
}
```

**INI**
```
[database]
host = localhost
port = 5432

[settings]
debug = true
```
