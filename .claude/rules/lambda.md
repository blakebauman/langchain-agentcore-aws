---
paths:
  - "src/agentic_ai/lambda_handlers/**/*.py"
---

# Lambda Handler Conventions

- Handlers route by `event["apiPath"]`. Add new endpoints by extending the if/elif chain.
- Response format must match Bedrock Agent action group spec: `{"messageVersion": "1.0", "response": {"actionGroup": ..., "apiPath": ..., "httpMethod": ..., "httpStatusCode": 200, "responseBody": {"application/json": {"body": ...}}}}`.
- When adding a new action endpoint, also update the OpenAPI schema in `infra/modules/bedrock-agent/main.tf`.
- Lambda functions have no VPC attachment by default. If a tool needs VPC resources, update the Lambda module.
