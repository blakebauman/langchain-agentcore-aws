"""Lambda handler for Bedrock Agent action groups.

This handler is invoked by a Bedrock Agent when it decides to use an action group.
It routes requests based on the apiPath and returns responses in the format
expected by Bedrock Agents.

Deploy this as a Lambda function and reference it in the Bedrock Agent action group
Terraform configuration.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Bedrock Agent action group Lambda handler.

    Args:
        event: Bedrock Agent invocation event containing apiPath, parameters, etc.
        context: Lambda context object.
    """
    api_path = event.get("apiPath", "")
    http_method = event.get("httpMethod", "GET")
    parameters = {p["name"]: p["value"] for p in event.get("parameters", [])}
    request_body = event.get("requestBody", {})

    logger.info("Action group request: %s %s params=%s", http_method, api_path, parameters)

    try:
        result = _route_request(api_path, http_method, parameters, request_body)
    except Exception:
        logger.exception("Error handling action group request")
        result = {"error": "Internal error processing request"}

    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", ""),
            "apiPath": api_path,
            "httpMethod": http_method,
            "httpStatusCode": 200,
            "responseBody": {"application/json": {"body": json.dumps(result)}},
        },
    }


def _route_request(
    api_path: str,
    http_method: str,
    parameters: dict[str, str],
    request_body: dict[str, Any],
) -> dict[str, Any]:
    """Route the request to the appropriate handler based on apiPath.

    Add your action group endpoints here.
    """
    if api_path == "/calculate":
        expression = parameters.get("expression", "")
        # Import calculator logic from tools
        from agentic_ai.tools.calculator import calculator

        result = calculator.invoke(expression)
        return {"result": result}

    if api_path == "/health":
        return {"status": "healthy"}

    return {"error": f"Unknown endpoint: {http_method} {api_path}"}
