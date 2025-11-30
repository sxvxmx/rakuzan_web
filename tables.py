import requests
import os
from typing import List, Union

api_token = os.getenv("MWS_API_TOKEN", "uskIkjuENVXWmuuEPPvQA2T")


def read_table(table_id, view=None, field_key=None):
    """
    Read records from a MWS table

    Args:
        table_id (str): The table ID
        view (str, optional): The view ID
        field_key (str, optional): The field key for filtering

    Returns:
        dict: The API response containing records
    """

    # Construct the URL
    base_url = f"https://tables.mws.ru/fusion/v1/datasheets/{table_id}/records"
    params = {}

    if view:
        params["viewId"] = view
    if field_key:
        params["fieldKey"] = field_key

    # Add parameters to URL if any
    if params:
        import urllib.parse

        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
    else:
        url = base_url

    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"API request failed with status code {response.status_code}: {response.text}"
        )


def write_table(table_id, records, view=None, field_key=None):
    """
    Write records to a MWS table

    Args:
        table_id (str): The table ID
        records (list): List of records to write, each record should have a 'fields' key
        view (str, optional): The view ID
        field_key (str, optional): The field key for filtering

    Returns:
        dict: The API response
    """

    # Construct the URL
    base_url = f"https://tables.mws.ru/fusion/v1/datasheets/{table_id}/records"
    params = {}

    if view:
        params["viewId"] = view
    if field_key:
        params["fieldKey"] = field_key

    # Add parameters to URL if any
    if params:
        import urllib.parse

        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
    else:
        url = base_url

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {"records": records}

    if field_key:
        payload["fieldKey"] = field_key

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"API request failed with status code {response.status_code}: {response.text}"
        )


def delete_table(table_id, record_ids: Union[str, List[str]], view=None):
    """
    Delete records from a MWS table

    Args:
        table_id (str): The table ID
        record_ids (str or list): Single record ID or list of record IDs to delete
        view (str, optional): The view ID

    Returns:
        dict: The API response
    """

    # Convert single record_id to list
    if isinstance(record_ids, str):
        record_ids = [record_ids]

    # Construct the URL
    base_url = f"https://tables.mws.ru/fusion/v1/datasheets/{table_id}/records"
    params = {}

    # Add record IDs to params (multiple recordIds parameters)
    params["recordIds"] = record_ids

    if view:
        params["viewId"] = view

    # Build query string manually to handle multiple recordIds
    import urllib.parse

    query_parts = []
    for record_id in record_ids:
        query_parts.append(f"recordIds={urllib.parse.quote(record_id)}")

    if view:
        query_parts.append(f"viewId={urllib.parse.quote(view)}")

    url = f"{base_url}?{'&'.join(query_parts)}"

    headers = {"Authorization": f"Bearer {api_token}"}

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"API request failed with status code {response.status_code}: {response.text}"
        )


def update_table(table_id, records, view=None, field_key=None):
    """
    Write records to a MWS table

    Args:
        table_id (str): The table ID
        records (list): List of records to write, each record should have a 'fields' key
        view (str, optional): The view ID
        field_key (str, optional): The field key for filtering

    Returns:
        dict: The API response
    """

    # Construct the URL
    base_url = f"https://tables.mws.ru/fusion/v1/datasheets/{table_id}/records"
    params = {}

    if view:
        params["viewId"] = view
    if field_key:
        params["fieldKey"] = field_key

    # Add parameters to URL if any
    if params:
        import urllib.parse

        query_string = urllib.parse.urlencode(params)
        url = f"{base_url}?{query_string}"
    else:
        url = base_url

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    payload = {"records": records}

    if field_key:
        payload["fieldKey"] = field_key

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"API request failed with status code {response.status_code}: {response.text}"
        )
