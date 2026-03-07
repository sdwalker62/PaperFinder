# PaperFinder

Automated ML/AI paper and blog discovery, summarization, and delivery system.

PaperFinder scrapes arXiv, Google DeepMind Blog, Anthropic Blog, and other configurable sources for new papers and posts. It uses **AWS Bedrock** (Claude) to score relevance against your topics of interest, generates concise summaries, builds a PDF digest, and delivers it via email (SES) on a daily schedule. Optional Discord webhook integration is included.

## Features

- **Multi-source scraping** — RSS feeds (arXiv, OpenAI, HuggingFace, Microsoft Research) and HTML blogs (DeepMind, Anthropic, Meta AI)
- **arXiv HTML5 links** — arXiv paper links are automatically rewritten to the HTML5 full-text version
- **LLM-powered ranking** — LiteLLM scores each paper's relevance to your configured topics (supports Bedrock, OpenAI, Anthropic, and more)
- **LLM-generated summaries** — Concise 3-5 paragraph summaries for the top papers with per-run budget guardrails
- **PDF digest** — A formatted PDF report generated daily via ReportLab
- **Email delivery** — Sent via AWS SES with the PDF as an attachment
- **Discord integration** — Optional webhook posting for team channels
- **Configurable** — Topics, sources, schedule, and limits all defined in YAML
- **AWS-native** — Deployable as a Lambda function with SAM, or as a Docker container on ECS/Fargate

## Project Structure

```
PaperFinder/
├── config/
│   ├── settings.yaml        # Topics, schedule, email, AWS, Discord config
│   └── sources.yaml         # List of websites/feeds to scrape
├── src/paperfinder/
│   ├── __init__.py
│   ├── cli.py               # CLI entry point (run / serve / scrape-only)
│   ├── config.py            # Configuration loading & Pydantic models
│   ├── discord_bot.py       # Discord webhook integration
│   ├── email_sender.py      # AWS SES email delivery
│   ├── lambda_handler.py    # AWS Lambda handler for SAM deployment
│   ├── llm.py               # LiteLLM integration (provider-agnostic + budget guard)
│   ├── models.py            # Domain models (Paper dataclass)
│   ├── pdf.py               # PDF generation (ReportLab)
│   ├── pipeline.py          # Main orchestrator
│   ├── scheduler.py         # Daily scheduler
│   └── scrapers.py          # RSS & HTML scrapers
├── tests/                   # Unit tests (pytest)
├── .github/workflows/ci.yaml
├── Dockerfile
├── template.yaml            # AWS SAM template
└── pyproject.toml
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- AWS account with Bedrock and SES enabled
- AWS credentials configured (`~/.aws/credentials` or env vars)

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/dalton/PaperFinder.git
cd PaperFinder
uv sync
```

### Configuration

Edit `config/settings.yaml` to set your topics, email, and AWS region. Edit `config/sources.yaml` to add or remove scraping sources.

Environment variables can override any setting using the `PAPERFINDER_` prefix with `__` as a nested delimiter:

```bash
export PAPERFINDER_EMAIL__SENDER="me@example.com"
export PAPERFINDER_EMAIL__RECIPIENTS='["me@example.com"]'
export PAPERFINDER_AWS__REGION="us-west-2"
```

### Usage

```bash
# Run the full pipeline once
paperfinder run

# Start the daily scheduler
paperfinder serve

# Scrape sources without LLM/delivery (debug mode)
paperfinder scrape-only
```

## Deployment

### Docker

```bash
docker build -t paperfinder .
docker run -e AWS_ACCESS_KEY_ID=... -e AWS_SECRET_ACCESS_KEY=... paperfinder
```

### AWS Lambda (SAM)

```bash
sam build
sam deploy --guided \
  --parameter-overrides \
    SenderEmail=me@example.com \
    RecipientEmail=me@example.com
```

## Testing

```bash
uv run pytest                    # Run all tests
uv run pytest --cov              # With coverage report
uv run ruff check src/ tests/    # Linting
uv run mypy src/paperfinder/     # Type checking
```

## CI/CD

The GitHub Actions pipeline (`.github/workflows/ci.yaml`) runs on every push and PR:

1. **Lint & Type Check** — Ruff + Mypy
2. **Tests** — pytest across Python 3.11, 3.12, 3.13
3. **Docker Build** — Builds and smoke-tests the container
4. **Deploy** *(main branch only)* — `sam build` + `sam deploy` to AWS Lambda

### Required GitHub configuration

| Type | Name | Description |
|------|------|-------------|
| Secret | `AWS_DEPLOY_ROLE_ARN` | IAM role ARN for OIDC-based deployment |
| Secret | `SES_SENDER_EMAIL` | Verified SES sender address |
| Secret | `SES_RECIPIENT_EMAIL` | Recipient email address |
| Variable | `AWS_REGION` | AWS region (default: `us-east-1`) |
| Variable | `LLM_MODEL` | LiteLLM model string (default: `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0`) |
| Variable | `LLM_MAX_BUDGET_USD` | Per-run budget cap (default: `1.00`) |

Set these under **Settings → Secrets and variables → Actions** in your GitHub repo. The deploy job uses a `production` environment, so you can also add environment-level protection rules (approvals, delay timers, etc.).

## License

MIT
