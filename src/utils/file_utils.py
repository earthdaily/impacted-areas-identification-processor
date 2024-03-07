# -*- coding: utf-8 -*-

"""Utility functions for file operations."""
import json

from pydantic import ValidationError

from schemas.input_schema import InputModel
from schemas.output_schema import OutputModel


def validate_data(data, data_type):
    """
    Validate data against the specified schema.

    Args:
        data (dict): The data to validate.
        data_type (str): The type of data ('input' or 'output').

    Raises:
        ValueError: If the data_type is not 'input' or 'output'.
        ValidationError: If the data does not conform to the specified schema.
    """
    try:
        if data_type == "input":
            InputModel(**data)
        elif data_type == "output":
            OutputModel(**data)
        else:
            raise ValueError("Invalid data_type. Must be 'input' or 'output'.")
    except ValidationError as e:
        print(f"Pydantic validation error: {e}")
        raise


def load_input_data(input_data_path):
    """
    Load input data from the specified file.

    Args:
        input_data_path (str): The path to the input data file.

    Returns:
        dict: The loaded input data.
    """
    try:
        with open(input_data_path, "r", encoding="utf-8") as file:
            input_data = json.load(file)
        return input_data
    except FileNotFoundError:
        print(f"File '{input_data_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise
