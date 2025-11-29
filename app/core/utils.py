from typing import Any

def format_response(data: Any, message: str = "Success", status_code: int = 200) -> dict:
    return {
        "status_code": status_code,
        "message": message,
        "data": data
    }

def format_error(message: str, status_code: int = 400) -> dict:
    return {
        "status_code": status_code,
        "message": message,
        "data": None
    }
