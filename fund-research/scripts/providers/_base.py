_DATA_STATUS = {}


def _record_status(key: str, success: bool, detail: str = "", source: str = "AKShare"):
    _DATA_STATUS[key] = {"success": success, "detail": detail, "source": source}


def get_data_status() -> dict:
    return dict(_DATA_STATUS)
