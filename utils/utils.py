import re

def parse_boolean_from_response(response):
    """
    Converts string 'True' or 'False' from model response to actual boolean.
    """
    match = re.fullmatch(r"True|False", response.strip())
    if match:
        return response.strip() == "True"
    else:
        raise ValueError(f"Unexpected response format: {response}")
