from __future__ import annotations

from typing import Any, Dict

import requests

class OPAError(RuntimeError):
    pass

def query_opa(*, url: str, timeout_seconds: float, input_payload: Dict[str, Any]) -> bool:
    """
    Calls OPA's data API endpoint that returns {"result": true/false}.
    """
    try:
        resp = requests.post(url, json={"input": input_payload}, timeout=timeout_seconds)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        raise OPAError(f"OPA request failed: {exc}") from exc

    result = data.get("result")
    if not isinstance(result, bool):
        raise OPAError(f"OPA response missing boolean result: {data}")
    return result
