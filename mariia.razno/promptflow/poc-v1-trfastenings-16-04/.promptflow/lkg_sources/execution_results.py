import json
import os
import logging
import re

from promptflow import tool

# Configure logging to use the level from PF_LOGGING_LEVEL or default to WARNING
@tool
def my_python_tool(sql_dict):
    # Parse the outer JSON
    num_products = re.findall(r"'num_products'\:\s*(\d+)", str(sql_dict))
    if len(num_products) > 0:
        extracted_num = int(num_products[0])
        if extracted_num <= 200 and extracted_num != 0:
            return 1
    return 0