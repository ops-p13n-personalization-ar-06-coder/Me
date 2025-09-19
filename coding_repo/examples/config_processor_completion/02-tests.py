import pytest
import tempfile
import os
import json
from solution import ConfigurationProcessor, ConfigurationError


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    import shutil
    shutil.rmtree(temp_dir)


@pytest.fixture
def schema():
    return {
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


def create_temp_file(temp_dir, filename: str, content: str):
    filepath = os.path.join(temp_dir, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


def test_load_json_file_success(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    content = '{"database": {"host": "localhost", "port": 5432}, "debug": true}'
    filepath = create_temp_file(temp_dir, "config.json", content)
    
    result = processor.load_config_file(filepath, "json")
    assert result == True
    assert len(processor.configurations) == 1
    assert processor.configurations[0]["database"]["host"] == "localhost"


def test_load_ini_file_success(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    content = """[database]
host = localhost
port = 5432

[settings]
debug = true
log_level = INFO"""
    filepath = create_temp_file(temp_dir, "config.ini", content)
    
    result = processor.load_config_file(filepath, "ini")
    assert result == True
    assert processor.configurations[0]["database"]["host"] == "localhost"
    assert processor.configurations[0]["settings"]["debug"] == True


def test_load_file_not_found(schema):
    processor = ConfigurationProcessor(schema)
    result = processor.load_config_file("nonexistent.json", "json")
    assert result == False


def test_load_invalid_json(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    content = '{"invalid": json}'
    filepath = create_temp_file(temp_dir, "invalid.json", content)
    
    result = processor.load_config_file(filepath, "json")
    assert result == False


def test_load_invalid_format(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    content = '{"valid": "json"}'
    filepath = create_temp_file(temp_dir, "config.json", content)
    
    result = processor.load_config_file(filepath, "xml")
    assert result == False


def test_merge_configurations_deep_merge(schema):
    processor = ConfigurationProcessor(schema)
    processor.configurations = [
        {"database": {"host": "localhost", "port": 5432}},
        {"database": {"port": 3306, "username": "admin"}}
    ]
    
    result = processor.merge_configurations()
    expected = {
        "database": {
            "host": "localhost",
            "port": 3306,
            "username": "admin"
        }
    }
    assert result == expected


def test_merge_configurations_list_replacement(schema):
    processor = ConfigurationProcessor(schema)
    processor.configurations = [
        {"features": ["feature1", "feature2"]},
        {"features": ["feature3"]}
    ]
    
    result = processor.merge_configurations()
    assert result["features"] == ["feature3"]


def test_merge_configurations_empty(schema):
    processor = ConfigurationProcessor(schema)
    result = processor.merge_configurations()
    assert result == {}


def test_validate_configuration_success(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "admin"
        },
        "debug": True,
        "log_level": "DEBUG",
        "timeout": 10.5,
        "features": ["auth", "logging"]
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == True
    assert errors == []


def test_validate_configuration_missing_required(schema):
    processor = ConfigurationProcessor(schema)
    config = {"debug": True}
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Required field 'database' is missing" in errors


def test_validate_configuration_wrong_type(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "port": "invalid_port"
        }
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database.port' must be integer, got str" in errors


def test_validate_configuration_value_range_min(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "port": 0
        }
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database.port' value 0 is below minimum 1" in errors


def test_validate_configuration_value_range_max(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "port": 70000
        }
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database.port' value 70000 is above maximum 65535" in errors


def test_validate_configuration_string_length(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "username": "ab"
        }
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database.username' length 2 is below minimum 3" in errors


def test_validate_configuration_allowed_values(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "log_level": "INVALID"
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'log_level' value 'INVALID' not in allowed values ['DEBUG', 'INFO', 'WARNING', 'ERROR']" in errors


def test_validate_configuration_list_length(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "features": []
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'features' length 0 is below minimum 1" in errors


def test_validate_configuration_float_type(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "timeout": "not_a_number"
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'timeout' must be float, got str" in errors


def test_transform_values_type_coercion(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "port": "3306"
        },
        "timeout": "15.5",
        "debug": "true"
    }
    
    result = processor.transform_values(config)
    assert result["database"]["port"] == 3306
    assert result["timeout"] == 15.5
    assert result["debug"] == True


def test_transform_values_defaults(schema):
    processor = ConfigurationProcessor(schema)
    config = {"database": {"host": "localhost"}}
    
    result = processor.transform_values(config)
    assert result["debug"] == False
    assert result["log_level"] == "INFO"
    assert result["database"]["port"] == 5432


def test_transform_values_string_transforms(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "log_level": "debug",
        "name": "  test  "
    }
    
    result = processor.transform_values(config)
    assert result["log_level"] == "DEBUG"
    assert result["name"] == "test"


def test_transform_values_numeric_transforms():
    schema = {"value": {"type": "integer", "transform": "abs"}}
    processor = ConfigurationProcessor(schema)
    config = {"value": -10}
    
    result = processor.transform_values(config)
    assert result["value"] == 10


def test_ini_parsing_float_values(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    content = """[database]
host = localhost
port = 5432

[settings]
timeout = 15.5
debug = true"""
    filepath = create_temp_file(temp_dir, "float_test.ini", content)
    
    result = processor.load_config_file(filepath, "ini")
    assert result == True
    config = processor.configurations[0]
    assert config["settings"]["timeout"] == 15.5
    assert config["settings"]["debug"] == True


def test_process_all_success(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    json_content = '{"database": {"host": "localhost"}, "debug": true}'
    ini_content = """[database]
username = admin"""
    
    json_path = create_temp_file(temp_dir, "base.json", json_content)
    ini_path = create_temp_file(temp_dir, "override.ini", ini_content)
    
    processor.load_config_file(json_path, "json")
    processor.load_config_file(ini_path, "ini")
    
    result = processor.process_all()
    assert result["database"]["host"] == "localhost"
    assert result["database"]["port"] == 5432
    assert result["database"]["username"] == "admin"
    assert result["debug"] == True
    assert result["log_level"] == "INFO"


def test_process_all_validation_failure(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    json_content = '{"debug": true}'
    json_path = create_temp_file(temp_dir, "invalid.json", json_content)
    
    processor.load_config_file(json_path, "json")
    
    with pytest.raises(ConfigurationError) as exc_info:
        processor.process_all()
    
    assert "Configuration validation failed:" in str(exc_info.value)
    assert "Required field 'database' is missing" in str(exc_info.value)


def test_multiple_validation_errors(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "log_level": "INVALID",
        "timeout": 100.0,
        "features": []
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert len(errors) == 4
    assert "Required field 'database' is missing" in errors
    assert "Field 'log_level' value 'INVALID' not in allowed values ['DEBUG', 'INFO', 'WARNING', 'ERROR']" in errors
    assert "Field 'timeout' value 100.0 is above maximum 30.0" in errors
    assert "Field 'features' length 0 is below minimum 1" in errors


def test_nested_schema_validation():
    schema = {
        "app": {
            "type": "dict",
            "nested_schema": {
                "database": {
                    "type": "dict",
                    "nested_schema": {
                        "host": {"type": "string", "required": True}
                    }
                }
            }
        }
    }
    processor = ConfigurationProcessor(schema)
    config = {"app": {"database": {}}}
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Required field 'app.database.host' is missing" in errors


def test_transform_nested_defaults():
    schema = {
        "app": {
            "type": "dict",
            "nested_schema": {
                "name": {"type": "string", "default": "MyApp"},
                "version": {"type": "string", "default": "1.0.0"}
            }
        }
    }
    processor = ConfigurationProcessor(schema)
    config = {"app": {}}
    
    result = processor.transform_values(config)
    assert result["app"]["name"] == "MyApp"
    assert result["app"]["version"] == "1.0.0"


def test_transform_lowercase_strip():
    schema = {
        "title": {"type": "string", "transform": "lowercase"},
        "description": {"type": "string", "transform": "strip"}
    }
    processor = ConfigurationProcessor(schema)
    config = {"title": "HELLO WORLD", "description": "  test  "}
    
    result = processor.transform_values(config)
    assert result["title"] == "hello world"
    assert result["description"] == "test"


def test_transform_nested_fields():
    schema = {
        "server": {
            "type": "dict",
            "nested_schema": {
                "name": {"type": "string", "transform": "uppercase"},
                "environment": {"type": "string", "transform": "lowercase"},
                "description": {"type": "string", "transform": "strip"},
                "config": {
                    "type": "dict", 
                    "nested_schema": {
                        "mode": {"type": "string", "transform": "uppercase"}
                    }
                }
            }
        }
    }
    processor = ConfigurationProcessor(schema)
    config = {
        "server": {
            "name": "web-server",
            "environment": "PRODUCTION",
            "description": "  Main web server  ",
            "config": {
                "mode": "debug"
            }
        }
    }
    
    result = processor.transform_values(config)
    assert result["server"]["name"] == "WEB-SERVER"
    assert result["server"]["environment"] == "production"
    assert result["server"]["description"] == "Main web server"
    assert result["server"]["config"]["mode"] == "DEBUG"


def test_validate_configuration_string_max_length(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {
            "host": "localhost",
            "username": "this_username_is_way_too_long_for_the_max_limit"
        }
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database.username' length 47 is above maximum 20" in errors


def test_validate_configuration_list_max_length():
    schema = {
        "database": {"type": "dict", "required": True, "nested_schema": {"host": {"type": "string", "required": True}}},
        "tags": {"type": "list", "max_length": 3}
    }
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'tags' length 5 is above maximum 3" in errors


def test_validate_configuration_boolean_type(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "debug": "not_a_boolean"
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'debug' must be boolean, got str" in errors


def test_validate_configuration_list_type(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": {"host": "localhost"},
        "features": "not_a_list"
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'features' must be list, got str" in errors


def test_validate_configuration_dict_type(schema):
    processor = ConfigurationProcessor(schema)
    config = {
        "database": "not_a_dict"
    }
    
    is_valid, errors = processor.validate_configuration(config)
    assert is_valid == False
    assert "Field 'database' must be dict, got str" in errors


def test_process_all_multiple_validation_errors(schema, temp_dir):
    processor = ConfigurationProcessor(schema)
    json_content = '{"debug": 123, "log_level": "INVALID_LEVEL", "timeout": 100.0, "features": []}'
    json_path = create_temp_file(temp_dir, "invalid_multiple.json", json_content)
    
    processor.load_config_file(json_path, "json")
    
    with pytest.raises(ConfigurationError) as exc_info:
        processor.process_all()
    
    error_message = str(exc_info.value)
    assert error_message.startswith("Configuration validation failed:")
    
    assert "Required field 'database' is missing" in error_message
    assert "Field 'debug' must be boolean, got int" in error_message
    assert "Field 'log_level' value 'INVALID_LEVEL' not in allowed values" in error_message
    assert "Field 'timeout' value 100.0 is above maximum 30.0" in error_message
    assert "Field 'features' length 0 is below minimum 1" in error_message
    
    errors_part = error_message[len("Configuration validation failed: "):]
    error_list = errors_part.split("; ")
    assert len(error_list) == 5


def test_boundary_conditions_numeric_ranges():
    schema = {
        "database": {
            "type": "dict",
            "required": True,
            "nested_schema": {
                "host": {"type": "string", "required": True},
                "port": {"type": "integer", "min_value": 1, "max_value": 65535}
            }
        }
    }
    processor = ConfigurationProcessor(schema)
    
    config_min = {"database": {"host": "localhost", "port": 1}}
    is_valid, errors = processor.validate_configuration(config_min)
    assert is_valid == True
    assert len(errors) == 0
    
    config_max = {"database": {"host": "localhost", "port": 65535}}
    is_valid, errors = processor.validate_configuration(config_max)
    assert is_valid == True
    assert len(errors) == 0


def test_boundary_conditions_string_length():
    schema = {
        "database": {
            "type": "dict",
            "required": True,
            "nested_schema": {
                "host": {"type": "string", "required": True},
                "username": {"type": "string", "min_length": 3, "max_length": 20}
            }
        }
    }
    processor = ConfigurationProcessor(schema)
    
    config_min = {"database": {"host": "localhost", "username": "abc"}}
    is_valid, errors = processor.validate_configuration(config_min)
    assert is_valid == True
    assert len(errors) == 0
    
    config_max = {"database": {"host": "localhost", "username": "a" * 20}}
    is_valid, errors = processor.validate_configuration(config_max)
    assert is_valid == True
    assert len(errors) == 0


def test_boundary_conditions_list_length():
    schema = {
        "database": {"type": "dict", "required": True, "nested_schema": {"host": {"type": "string", "required": True}}},
        "features": {"type": "list", "min_length": 1, "max_length": 5}
    }
    processor = ConfigurationProcessor(schema)
    
    config_min = {"database": {"host": "localhost"}, "features": ["feature1"]}
    is_valid, errors = processor.validate_configuration(config_min)
    assert is_valid == True
    assert len(errors) == 0
    
    config_max = {"database": {"host": "localhost"}, "features": ["f1", "f2", "f3", "f4", "f5"]}
    is_valid, errors = processor.validate_configuration(config_max)
    assert is_valid == True
    assert len(errors) == 0

def test_boundary_conditions_float_ranges():
    schema = {
        "database": {"type": "dict", "required": True, "nested_schema": {"host": {"type": "string", "required": True}}},
        "timeout": {"type": "float", "min_value": 0.1, "max_value": 30.0}
    }
    processor = ConfigurationProcessor(schema)
    
    config_min = {"database": {"host": "localhost"}, "timeout": 0.1}
    is_valid, errors = processor.validate_configuration(config_min)
    assert is_valid == True
    assert len(errors) == 0
    
    config_max = {"database": {"host": "localhost"}, "timeout": 30.0}
    is_valid, errors = processor.validate_configuration(config_max)
    assert is_valid == True
    assert len(errors) == 0

@pytest.mark.parametrize("boolean_string,expected", [
    ("true", True), ("True", True), ("TRUE", True), ("1", True), ("yes", True),
    ("Yes", True), ("YES", True), ("on", True), ("On", True), ("ON", True),
    ("false", False), ("False", False), ("FALSE", False), ("0", False), ("no", False),
    ("No", False), ("NO", False), ("off", False), ("Off", False), ("OFF", False),
    ("random_string", False), ("", False), ("2", False), ("anything_else", False)
])
def test_transform_boolean_coercion_comprehensive(boolean_string, expected):
    schema = {"debug": {"type": "boolean"}}
    processor = ConfigurationProcessor(schema)
    config = {"debug": boolean_string}
    
    result = processor.transform_values(config)
    assert result["debug"] == expected


def test_transform_failed_coercion_unchanged():
    schema = {
        "port": {"type": "integer"},
        "timeout": {"type": "float"},
        "count": {"type": "integer"}
    }
    processor = ConfigurationProcessor(schema)
    config = {
        "port": "not_a_number",
        "timeout": "invalid_float", 
        "count": "abc123"
    }
    
    result = processor.transform_values(config)
    assert result["port"] == "not_a_number"
    assert result["timeout"] == "invalid_float"
    assert result["count"] == "abc123"


def test_transform_any_to_string_coercion():
    schema = {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "title": {"type": "string"},
        "label": {"type": "string"}
    }
    processor = ConfigurationProcessor(schema)
    config = {
        "name": 123, "description": 45.67, "title": True, "label": ["a", "b"]
    }
    
    result = processor.transform_values(config)
    assert result["name"] == "123"
    assert result["description"] == "45.67"
    assert result["title"] == "True"
    assert result["label"] == "['a', 'b']"
