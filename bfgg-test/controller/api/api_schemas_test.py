import unittest
from marshmallow import ValidationError
from bfgg.controller.api.api_schemas import StartSchema, CloneSchema


class ApiSchemasTest(unittest.TestCase):

    def test_start_schema_valid_input(self):
        try:
            StartSchema().load({
                'project': 'my-project',
                'testClass': 'test-class',
                'javaOpts': 'java-opts'
            })
        except ValidationError:
            self.fail('Validation unsuccessful, test failed')

    def test_start_schema_valid_input_1(self):
        try:
            StartSchema().load({
                'project': 'my-project',
                'testClass': 'test-class'
            })
        except ValidationError:
            self.fail('Validation unsuccessful, test failed')

    def test_start_schema_invalid_input(self):
        with self.assertRaises(ValidationError):
            StartSchema().load({
                'project': 'my-project',
                'javaOpts': 'java-opts'
            })

    def test_start_schema_invalid_input_1(self):
        with self.assertRaises(ValidationError):
            StartSchema().load({
                'project1': 'my-project',
                'testClass': 'test-class',
                'javaOpts': 'java-opts'
            })

    def test_clone_schema_valid_input(self):
        try:
            CloneSchema().load({
                'repo': 'git@github.com:bee-anchor/bfgg.git'
            })
        except ValidationError:
            self.fail('Validation unsuccessful, test failed')

    def test_clone_schema_valid_input_1(self):
        try:
            CloneSchema().load({
                'repo': 'git@github.com:bee-anchor/bfgg.git'
            })
        except ValidationError:
            self.fail('Validation unsuccessful, test failed')

    def test_clone_schema_valid_input_2(self):
        try:
            CloneSchema().load({
                'repo': 'git@github.com:bee-anchor/bfgg.git/'
            })
        except ValidationError:
            self.fail('Validation unsuccessful, test failed')

    def test_clone_schema_invalid_input(self):
        with self.assertRaises(ValidationError):
            CloneSchema().load({
                'repo1': 'git@github.com:bee-anchor/bfgg.git'
            })

    def test_clone_schema_invalid_input_1(self):
        with self.assertRaises(ValidationError):
            CloneSchema().load({
                'repo': 'git@github.com:bee-anchor/bfgg.gi'
            })

    def test_clone_schema_invalid_input_2(self):
        with self.assertRaises(ValidationError):
            CloneSchema().load({
                'repo': 'it@github.com:bee-anchor/bfgg.git'
            })


if __name__ == '__main__':
    unittest.main()
