import copy
import json
import unittest
from typing import Union, Iterable, Any, Hashable

import jsonschema


class NestedValueException(Exception):
    pass


def get_nested_value(o: Union[list, dict], path: list[Hashable]) -> Any:
    working = o
    for key in path:
        working = working[key]
    return working


def set_nested_value(o: Union[list, dict], path: list[Hashable], new_value: Any) -> None:
    if len(path) == 0:
        raise NestedValueException("Path can't be empty!")
    working = get_nested_value(o, path[:-1])
    working[path[-1]] = new_value


def del_nested_value(o: Union[list, dict], path: list[Hashable]) -> None:
    if len(path) == 0:
        raise NestedValueException("Path can't be empty!")
    working = get_nested_value(o, path[:-1])
    del working[path[-1]]


class TestNestedValueMethods(unittest.TestCase):
    def test_get_nested_value(self):
        base = {"a": [0], "b": [1, 2], "c": [3, 4, 5]}
        for path, expected in [
            ([], base),
            (["a"], [0]),
            (["a", 0], 0),
            (["b", 0], 1),
            (["c", 2], 5),
        ]:
            self.assertEqual(result := get_nested_value(base, path), expected,
                             msg=f'Path "{path}" returned {result}, not {expected}')

    def test_set_nested_value(self):
        base = {"a": [0], "b": [1, 2], "c": [3, 4, 5]}
        new_value = "_"
        for path, expected in [
            (["a"], {"a": new_value, "b": [1, 2], "c": [3, 4, 5]}),
            (["a", 0], {"a": [new_value], "b": [1, 2], "c": [3, 4, 5]}),
            (["b", 0], {"a": [0], "b": [new_value, 2], "c": [3, 4, 5]}),
            (["c", 2], {"a": [0], "b": [1, 2], "c": [3, 4, new_value]}),
        ]:
            base_copy = copy.deepcopy(base)
            set_nested_value(base_copy, path, new_value)
            self.assertEqual(base_copy, expected,
                             msg=f'Returned {base_copy}, not {expected}')

    def test_set_nested_value_empty_exception(self):
        with self.assertRaises(NestedValueException):
            set_nested_value({}, [], "")

    def test_del_nested_value_empty_exception(self):
        with self.assertRaises(NestedValueException):
            del_nested_value({}, [])


class TestConfig(unittest.TestCase):
    def test_example(self):
        with open("config_schema.json", "rb") as f:
            schema = json.load(f)
        with open("example_config.json", "rb") as f:
            example = json.load(f)

        try:
            jsonschema.validate(example, schema)
        except jsonschema.exceptions.ValidationError:
            self.fail(f"Example doesn't pass validation!")

    def test_schema_invalids(self):
        # Load
        with open("config_schema.json", "rb") as f:
            schema = json.load(f)
        with open("example_config.json", "rb") as f:
            base = json.load(f)

        # Iterate
        for n, (path, invalid_value, valid_value) in enumerate([
            (["images"], {}, {"desktop": {"width": 2560, "height": 1440}}),
            (["images"], {"desktop": {"width": 2560, "height": 1440, "burp": 1}},
             {"desktop": {"width": 2560, "height": 1440}}),
            (["images", "desktop"], {"width": 2560}, {"width": 2560, "height": 1440}),
            (["images", "desktop"], {}, {"width": 2560, "height": 1440}),
            (["images", "desktop"], {"width": 2560, "height": 1440, "burp": 1}, {"width": 2560, "height": 1440}),
            (["images", "desktop", "width"], -1, 1),
            (["images", "desktop", "height"], -1, 1),
            (["images", "desktop", "width"], 1.1, 1),
            (["images", "desktop", "height"], 1.1, 1),
        ]):
            # Use a copy so that later tests work too
            base_copy = copy.deepcopy(base)

            # Test invalid value
            # This is what we really care about
            set_nested_value(base_copy, path, invalid_value)
            with self.assertRaises(jsonschema.exceptions.ValidationError,
                                   msg=f'{invalid_value} in {path} should be invalid!\nFinal structure is {base_copy}'):
                jsonschema.validate(base_copy, schema)

            # Test valid value
            # This is mainly here to ensure the above isn't passing because it's being inserted into the wrong place
            # Because the same value is overwritten, a second copy isn't needed
            set_nested_value(base_copy, path, valid_value)
            try:
                jsonschema.validate(base_copy, schema)
            except jsonschema.exceptions.ValidationError:
                self.fail(f"Check {n}'s valid_value({valid_value} in {path}) shouldn't have raised an exception!")


if __name__ == '__main__':
    unittest.main()
