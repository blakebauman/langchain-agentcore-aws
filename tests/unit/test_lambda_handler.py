"""Tests for the Bedrock Agent action group Lambda handler."""

import json

from agentic_ai.lambda_handlers.action_group_handler import handler


class TestActionGroupHandler:
    def test_calculate_endpoint(self) -> None:
        event = {
            "apiPath": "/calculate",
            "httpMethod": "GET",
            "actionGroup": "test-actions",
            "parameters": [{"name": "expression", "value": "2 + 3"}],
        }
        response = handler(event, None)

        assert response["messageVersion"] == "1.0"
        assert response["response"]["httpStatusCode"] == 200
        body = json.loads(response["response"]["responseBody"]["application/json"]["body"])
        assert body["result"] == "5.0"

    def test_health_endpoint(self) -> None:
        event = {
            "apiPath": "/health",
            "httpMethod": "GET",
            "actionGroup": "test-actions",
            "parameters": [],
        }
        response = handler(event, None)

        body = json.loads(response["response"]["responseBody"]["application/json"]["body"])
        assert body["status"] == "healthy"

    def test_unknown_endpoint(self) -> None:
        event = {
            "apiPath": "/unknown",
            "httpMethod": "GET",
            "actionGroup": "test-actions",
            "parameters": [],
        }
        response = handler(event, None)

        body = json.loads(response["response"]["responseBody"]["application/json"]["body"])
        assert "error" in body
