import ast
import os
from typing import Dict, List, Set, Union

import pandas as pd


def ensure_full_path(excel_file_name: str) -> str:
    # Find the project root directory (assuming this script is in the src folder)
    project_root = os.path.join(os.path.dirname(__file__), "..")

    # Construct the full path to the Excel file, relative to the project root
    full_excel_path = os.path.normpath(os.path.join(project_root, excel_file_name))

    # Ensure the directory exists
    os.makedirs(os.path.dirname(full_excel_path), exist_ok=True)

    return full_excel_path


def ensure_excel_file(excel_file_name: str, sheet_names: set) -> None:
    """Create an Excel file with the specified name."""

    # Construct the full path to the Excel file, relative to the project root
    full_excel_path = ensure_full_path(excel_file_name)

    # Create an empty Excel file
    if not os.path.exists(full_excel_path):
        with pd.ExcelWriter(full_excel_path, engine="openpyxl") as writer:
            for sheet_name in sheet_names:
                pd.DataFrame().to_excel(writer, index=False, sheet_name=sheet_name)


def save_as_text_file(text: str, file_name: str):
    full_text_path = ensure_full_path(file_name)

    # Write the text to the file
    with open(full_text_path, "w") as file:
        file.write(text)


def delete_excel_file(excel_file_name: str) -> None:
    """Delete the specified Excel file."""

    # Construct the full path to the Excel file, relative to the project root
    full_excel_path = ensure_full_path(excel_file_name)

    # Delete the Excel file if it exists
    if os.path.exists(full_excel_path):
        os.remove(full_excel_path)


def load_excel_file(file_name: str, sheet_name: str) -> pd.DataFrame:
    """Load an Excel file and return the specified sheet as a DataFrame."""

    # Construct the full path to the Excel file, relative to the project root
    full_excel_path = ensure_full_path(file_name)

    # Load the specified sheet from the Excel file into a DataFrame
    try:
        with pd.ExcelFile(full_excel_path) as xls:
            if sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
            else:
                df = pd.DataFrame()
    except FileNotFoundError as e:
        df = pd.DataFrame()
        print(e)
        print("Creating new file.")

    return df


def find_row_by_id(df: pd.DataFrame, row_id: str) -> int:
    """Search for a row by author id and return its index."""
    indices = df.index[df["id"] == row_id].tolist()
    return indices[0] if indices else -1


def update_excel_file(
    file_name: str,
    sheet_name: str,
    data: Union[Dict[str, Union[str, int]], List[Dict[str, Union[str, int]]]],
    exclude_properties: Set[str] = set(),
    overwrite_sheet: bool = False,
) -> None:
    """
    Update an Excel file with new data.

    Parameters:
    - file_name (str): The name of the Excel file.
    - sheet_name (str): The name of the sheet in the Excel file.
    - data (Union[Dict[str, Union[str, int]], List[Dict[str, Union[str, int]]]]): The data to be added to the Excel file. It can be a dictionary or a list of dictionaries.
    - exclude_properties (Set[str], optional): A set of properties to exclude from the data. Defaults to an empty set.
    - overwrite_sheet (bool, optional): Whether to overwrite the existing sheet with the new data. Defaults to False.

    Returns:
    - None
    """
    # Construct the full path to the Excel file, relative to the project root
    full_excel_path = ensure_full_path(file_name)

    # Validate data argument as list of dicts
    data = data if isinstance(data, list) else [data]
    assert all(
        isinstance(d, dict) for d in data
    ), "'data' must be a dict or list of dicts"

    # Filter out the properties to exclude
    filtered_thread_data = [
        {key: value for key, value in row.items() if key not in exclude_properties}
        for row in data
    ]

    # Initialize DataFrame from the filtered data
    new_row_df = pd.DataFrame(filtered_thread_data)

    # Load the existing Excel file
    with pd.ExcelFile(full_excel_path) as xls:
        # If the sheet exists, read it into a DataFrame
        if sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
        else:
            # If the sheet doesn't exist, the new DataFrame becomes the sheet content
            df = pd.DataFrame()

    with pd.ExcelWriter(
        full_excel_path, engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        if overwrite_sheet:
            df = new_row_df
        else:
            df = pd.concat([df, new_row_df], ignore_index=True)
        # Write DataFrame to an Excel sheet
        df.to_excel(writer, sheet_name=sheet_name, index=False, engine="openpyxl")


def extract_from_excel(
    properties: dict, excel_file_name: str, sheet_name: str
) -> list[dict]:
    """
    Load rows from an Excel sheet with properties matching the provided dict.

    :param properties: A dictionary of properties to match.
    :param excel_file_name: The name of the Excel file.
    :param sheet_name: The name of the sheet to search within.
    :return: list of dicts containing the rows that match
    """
    # Load the Excel file
    df = load_excel_file(excel_file_name, sheet_name)

    if df.empty:
        return []

    # Create a boolean mask for each key-value pair in properties
    # and combine them with logical AND
    mask = pd.Series(True, index=df.index)
    for key, value in properties.items():
        mask &= df[key] == value
    filtered_df = df[mask].copy()

    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return []
    else:
        # run ast.literal_eval on each cell in the DataFrame
        # if the cell starts with a '[' or '{', it is a list or dict respectively
        # and needs to be evaluated
        for col in filtered_df.columns:
            filtered_df[col] = filtered_df[col].apply(
                lambda x: (
                    ast.literal_eval(x)
                    if isinstance(x, str)
                    and ((x.startswith("['") and x.endswith("']")) or x == "[]")
                    else x
                )
            )
        return filtered_df.to_dict("records")
