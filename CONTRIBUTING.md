# Contributing

Thanks for your interest in contributing to Agentic AI AWS! This guide will help you get started.

## Getting Started

1. Fork the repository and clone your fork
2. Install dependencies:
   ```bash
   make install
   ```
3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
4. See the [README](README.md) for AWS prerequisites (Bedrock access, Terraform, etc.)

## Development Workflow

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting, and [pytest](https://docs.pytest.org/) for testing. Pre-commit hooks are installed automatically by `make install`.

```bash
make fmt          # Auto-fix lint issues and format code
make lint         # Check for lint errors
make test         # Run unit tests with coverage
```

## Submitting Changes

1. Create a feature branch from `main`
2. Make your changes
3. Ensure `make lint` and `make test` pass
4. Open a pull request against `main`

Your PR should include:

- A clear description of the change and why it's needed
- Tests for new or changed behavior
- Documentation updates if applicable

Keep PRs focused — one feature or fix per PR.

## Bug Reports and Feature Requests

Use [GitHub Issues](../../issues) to report bugs or suggest features. We provide issue templates to help you include the right information.

**Bug reports** should include: steps to reproduce, expected vs. actual behavior, and your environment (Python version, OS, AWS region).

**Feature requests** should include: the use case, your proposed approach, and any alternatives you considered.

## Code Standards

- **Linting/Formatting**: ruff with `line-length = 100`, targeting Python 3.11+
- **Type hints**: Required on all function signatures
- **Tests**: Required for new functionality (see `tests/unit/` for examples)
- **Commits**: Use clear, descriptive commit messages

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
