import json
import re
import regex
from typing import Union, List, Dict


def parse_nested_json(json_string: str) -> Union[List, Dict]:
    """
    Parses a JSON string that may contain nested structures (objects or arrays).

    Args:
        json_string (str): The JSON string to parse.

    Returns:
        Union[List, Dict]: The parsed JSON object as a Python list or dictionary.

    Example:
        json_string = '''
        {
            "name": "John",
            "age": 30,
            "city": "New York",
            "pets": [
                {"name": "Fluffy", "type": "cat"},
                {"name": "Buddy", "type": "dog"}
            ]
        }
        '''

        parsed_json = parse_nested_json(json_string)
        print(parsed_json)

        Output:
        {
            'name': 'John',
            'age': 30,
            'city': 'New York',
            'pets': [
                {'name': 'Fluffy', 'type': 'cat'},
                {'name': 'Buddy', 'type': 'dog'}
            ]
        }
    """
    # Look for JSON object or array, supporting nested structures
    pattern = r"\[(?:[^[\]]|(?R))*\]|\{(?:[^{}]|(?R))*\}"

    # Find all potential JSON objects or arrays and pick the first one,
    # as we are assuming only one JSON object or array is present
    matched_json = regex.findall(pattern, json_string, regex.DOTALL)[0]

    # Unwrap the JSON string if it's wrapped by a fenced code block
    unwrapped_json = re.sub(r"```", "", matched_json)

    # Convert JSON string to a Python object (dict or list)
    parsed_json = json.loads(unwrapped_json)

    return parsed_json
