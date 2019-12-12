import pytest
from marshmallow import ValidationError

from bfgg.controller.api.api_schemas import StartSchema, CloneSchema


def test_start_schema_valid_input():
    try:
        StartSchema().load({
            'project': 'my-project',
            'testClass': 'test-class',
            'javaOpts': 'java-opts'
        })
    except ValidationError:
        pytest.fail('Validation unsuccessful, test failed')


def test_start_schema_valid_input_1():
    try:
        StartSchema().load({
            'project': 'my-project',
            'testClass': 'test-class'
        })
    except ValidationError:
        pytest.fail('Validation unsuccessful, test failed')


def test_start_schema_invalid_input():
    with pytest.raises(ValidationError):
        StartSchema().load({
            'project': 'my-project',
            'javaOpts': 'java-opts'
        })


def test_start_schema_invalid_input_1():
    with pytest.raises(ValidationError):
        StartSchema().load({
            'project1': 'my-project',
            'testClass': 'test-class',
            'javaOpts': 'java-opts'
        })


def test_clone_schema_valid_input():
    try:
        CloneSchema().load({
            'repo': 'git@github.com:bee-anchor/bfgg.git'
        })
    except ValidationError:
        pytest.fail('Validation unsuccessful, test failed')


def test_clone_schema_valid_input_1():
    try:
        CloneSchema().load({
            'repo': 'git@github.com:bee-anchor/bfgg.git'
        })
    except ValidationError:
        pytest.fail('Validation unsuccessful, test failed')


def test_clone_schema_valid_input_2():
    try:
        CloneSchema().load({
            'repo': 'git@github.com:bee-anchor/bfgg.git/'
        })
    except ValidationError:
        pytest.fail('Validation unsuccessful, test failed')


def test_clone_schema_invalid_input():
    with pytest.raises(ValidationError):
        CloneSchema().load({
            'repo1': 'git@github.com:bee-anchor/bfgg.git'
        })


def test_clone_schema_invalid_input_1():
    with pytest.raises(ValidationError):
        CloneSchema().load({
            'repo': 'git@github.com:bee-anchor/bfgg.gi'
        })


def test_clone_schema_invalid_input_2():
    with pytest.raises(ValidationError):
        CloneSchema().load({
            'repo': 'it@github.com:bee-anchor/bfgg.git'
        })
