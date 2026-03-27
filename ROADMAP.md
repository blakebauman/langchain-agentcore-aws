# Roadmap

Product and engineering roadmap for Agentic AI AWS. Items are organized by priority and grouped by theme. Check the box when completed.

## Completed

- [x] LangGraph ReAct agent with Bedrock Converse API (v0.1.0)
- [x] DeepAgent planning agent with sub-agent spawning (v0.1.0)
- [x] Bedrock AgentCore integration — Memory, Runtime, Gateway, Observability (v0.1.0)
- [x] Terraform modules — IAM, Bedrock Agent, Knowledge Base, Lambda, AgentCore (v0.1.0)
- [x] Tool registry — calculator, web search, KB retrieval, Gateway discovery (v0.1.0)
- [x] Chainlit chat UI with streaming, profiles, tool steps, file uploads (v0.2.0)
- [x] Chat persistence — InMemory, SQLite, AgentCore checkpointer (v0.2.0)
- [x] Conversation sidebar with SQLite data layer (v0.2.0)
- [x] Rate limiting per session (v0.2.0)
- [x] Health check endpoint for ECS/ALB (v0.3.0)
- [x] OpenTelemetry tracing in chat UI with AgentCore resource attributes (v0.3.0)
- [x] AWS Secrets Manager integration for production secrets (v0.3.0)
- [x] ALB with HTTPS/TLS 1.3 termination in Terraform (v0.3.0)

## In Progress

### Deploy to AWS
- [ ] Push container image to ECR
- [ ] Deploy chat service to ECS Fargate via Terraform
- [ ] Provision ACM certificate and configure DNS
- [ ] Validate end-to-end: ALB → ECS → Bedrock flow
- [ ] Set up CloudWatch alarms for error rates and latency

## Next Up

### Agent Capabilities
- [ ] **Real web search tool** — replace stub with Tavily or SerpAPI provider
- [ ] **Bedrock Guardrails** — content filtering and PII redaction on agent responses
- [ ] **Streaming tool results** — show partial tool output as it arrives
- [ ] **Agent memory across sessions** — use AgentCore MemoryStore for "remember my preferences"
- [ ] **Multi-model support** — let users pick Claude, Llama, Mistral from chat profile

### Authentication & Authorization
- [ ] **Cognito OAuth** — replace password auth with AWS Cognito user pools
- [ ] **Google/GitHub SSO** — social login via Cognito identity providers
- [ ] **Role-based access** — admin vs. user roles with different tool permissions

### Observability & Monitoring
- [ ] **Trace dashboard** — CloudWatch or Grafana dashboard for agent invocation metrics
- [ ] **Cost tracking** — log Bedrock token usage per conversation/user
- [ ] **Alerting** — CloudWatch alarms on error rate, latency P99, and Bedrock throttling
- [ ] **Audit log** — immutable record of all agent actions for compliance

### Infrastructure & Scaling
- [ ] **Auto-scaling** — ECS service auto-scaling based on CPU/connection count
- [ ] **WAF** — AWS WAF rules on ALB for bot protection and rate limiting at edge
- [ ] **VPC endpoints** — Bedrock VPC endpoint to keep traffic off the public internet
- [ ] **Multi-region** — active-passive failover for high availability
- [ ] **CDN** — CloudFront distribution for static chat assets

### Developer Experience
- [ ] **Integration tests** — end-to-end tests against a live Bedrock endpoint
- [ ] **Load testing** — Locust or k6 scripts for chat UI under concurrent users
- [ ] **Staging environment** — `infra/envs/staging/` with separate state
- [ ] **GitHub Actions deploy** — CI/CD pipeline for build → push → deploy
- [ ] **Pre-commit Terraform validate** — add `terraform validate` to pre-commit hooks

## Future Ideas

These are exploratory and may not be built. Listed for visibility.

- **Voice chat** — Chainlit audio support with Amazon Transcribe
- **Multi-agent collaboration** — agent-to-agent delegation via AgentCore A2A protocol
- **Knowledge base ingestion UI** — upload documents directly from chat to S3/KB
- **Custom tool builder** — UI for defining new tools without code
- **Conversation analytics** — aggregate stats on usage patterns, popular queries, tool usage
- **Mobile app** — React Native client consuming the same agent backend
