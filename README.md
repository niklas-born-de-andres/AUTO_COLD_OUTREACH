# Auto Cold Outreach

An automated cold outreach pipeline built for Kibo Ventures. Given a target contact and an assigned team member, the system researches the contact online, enriches the research with internal notes, drafts a personalized email using an LLM, and delivers it to the team member's Gmail inbox.

---

## Project Structure

- `main.py` — FastAPI app, exposes the single POST endpoint
- `orchestrator.py` — sequences the full pipeline from research to delivery
- `models.py` — Pydantic request and response models
- `services/contact_resolver.py` — validates contacts and team members against the CSV files
- `services/research.py` — runs three targeted Exa web searches per contact
- `services/research_validator.py` — filters raw research with Claude Haiku and enriches with internal notes
- `services/email_drafter.py` — generates the personalized email with Claude Sonnet
- `services/gmail_delivery.py` — delivers the draft to the team member's Gmail inbox
- `data/contacts.csv` — target contacts: first_name, last_name, company, notes
- `data/team.csv` — team members: name, email, role

---

## Prerequisites

- Python 3.9+
- A Google account with Gmail
- API keys for Exa and Anthropic

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/niklas-born-de-andres/AUTO_COLD_OUTREACH.git
cd AUTO_COLD_OUTREACH
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (Git Bash)
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
EXA_API_KEY=your_exa_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

- Exa: https://exa.ai/dashboard
- Anthropic: https://console.anthropic.com

### 5. Set up Gmail authentication

1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a new project
2. Enable the **Gmail API** under APIs & Services
3. Create an **OAuth Client ID** (Desktop app) under Credentials
   - If prompted, configure the consent screen first — choose **External**
4. Download the credentials file, rename it to `credentials.json`, and place it in the project root

On first run a browser window will open for Gmail authentication. A `token.json` file will be saved automatically after that. Do not commit either file.

---

## Running the API

```bash
uvicorn main:app --reload
```

API: `http://127.0.0.1:8000`
Swagger UI: `http://127.0.0.1:8000/docs`

---

## Usage

```bash
curl -X POST http://127.0.0.1:8000/generate-outreach \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Leonardo",
    "last_name": "Benini",
    "company": "Helmit",
    "team_member": "Nico"
  }'
```

### Response

```json
{
  "status": "delivered",
  "sent_to": "nico@kiboventures.com",
  "contact_name": "Leonardo Benini",
  "email_subject": "Helmit and Kibo Ventures",
  "email_preview": "Hi Leonardo, I'm Nico..."
}
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EXA_API_KEY` | Exa API key for web research |
| `ANTHROPIC_API_KEY` | Anthropic API key for email drafting and research validation |

Gmail uses `credentials.json` and `token.json` placed in the project root — not environment variables.

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `200` | Email successfully generated and delivered |
| `404` | Contact or team member not found in CSV |
| `500` | Unexpected error — check terminal logs for details |

---

## How It Works

```
POST /generate-outreach
        │
        ▼
1. ContactResolver      — validates contact and team member exist in CSVs
        │
        ▼
2. ResearchService      — searches the web for person background, recent activity,
                          and company news using the Exa API
        │
        ▼
3. ResearchValidatorService — filters raw research using an LLM (Claude Haiku),
                              removes wrong matches, enriches with internal notes
        │
        ▼
4. EmailDraftService    — generates a personalized email using Claude Sonnet
        │
        ▼
5. GmailDeliveryService — sends the draft to the team member's Gmail inbox
        │
        ▼
6. Returns confirmation + email preview
```

---

## Project Structure

```
AUTO_COLD_OUTREACH/
├── main.py                        # FastAPI app — single POST endpoint
├── orchestrator.py                # Sequences the full pipeline
├── models.py                      # Pydantic request and response models
├── config.py                      # Environment variable loading
├── services/
│   ├── contact_resolver.py        # CSV lookup for contacts and team members
│   ├── research.py                # Exa web search — 3 targeted queries per contact
│   ├── research_validator.py      # LLM-based research filtering and notes enrichment
│   ├── email_drafter.py           # Claude Sonnet email generation
│   └── gmail_delivery.py          # Gmail API delivery
├── data/
│   ├── contacts.csv               # Target contacts — first_name, last_name, company, notes
│   └── team.csv                   # Team members — name, email, role
├── .env.example                   # Environment variable template
├── requirements.txt               # Python dependencies
└── README.md
```

---

## Prerequisites

- Python 3.9+
- A Google account with Gmail
- API keys for Exa and Anthropic (see Setup)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/niklas-born-de-andres/AUTO_COLD_OUTREACH.git
cd AUTO_COLD_OUTREACH
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (Git Bash)
source .venv/Scripts/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

Open `.env` and add your keys:

```
EXA_API_KEY=your_exa_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Get your keys here:
- Exa: https://exa.ai/dashboard
- Anthropic: https://console.anthropic.com

### 5. Set up Gmail authentication

The system sends emails via the Gmail API using OAuth2. This requires a one-time setup:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (e.g. `auto-cold-outreach`)
3. Navigate to **APIs & Services → Library** and enable the **Gmail API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth Client ID**
   - If prompted, configure the OAuth consent screen first (choose **External**, fill in app name and your email)
   - Application type: **Desktop app**
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the project root

On first run, a browser window will open asking you to authenticate with Google. After authenticating, a `token.json` file will be generated automatically. Do not commit either file.

---

## Running the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

---

## Usage

Send a POST request to `/generate-outreach`:

```bash
curl -X POST http://127.0.0.1:8000/generate-outreach \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Leonardo",
    "last_name": "Benini",
    "company": "Helmit",
    "team_member": "Nico"
  }'
```

### Request body

| Field | Type | Description |
|-------|------|-------------|
| `first_name` | string | Contact's first name (must match contacts.csv) |
| `last_name` | string | Contact's last name (must match contacts.csv) |
| `company` | string | Contact's company (must match contacts.csv) |
| `team_member` | string | Team member who will receive the email draft (must match team.csv) |

### Response

```json
{
  "status": "delivered",
  "sent_to": "nico@kiboventures.com",
  "contact_name": "Leonardo Benini",
  "email_subject": "Helmit and Kibo Ventures",
  "email_preview": "Hi Leonardo, I'm Nico..."
}
```

---

## Data Files

### contacts.csv

Semicolon-delimited. UTF-8 encoded.

```
first_name;last_name;company;notes
Leonardo;Benini;Helmit;Co-founder at Helmit, TUM graduate, backed by EWOR. Pre-seed stage, raised $390k.
```

### team.csv

Semicolon-delimited. UTF-8 encoded.

```
name;email;role
Nico;nico@kiboventures.com;Product & Dev Intern
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EXA_API_KEY` | Exa API key for web research |
| `ANTHROPIC_API_KEY` | Anthropic API key for email drafting and research validation |

Gmail authentication uses `credentials.json` and `token.json` files in the project root — not environment variables.

---

## Error Handling

| Status | Meaning |
|--------|---------|
| `200` | Email successfully generated and delivered |
| `404` | Contact or team member not found in CSV files |
| `500` | Unexpected error — check terminal logs for details |

---

## Notes

- The first time the API runs, a browser window will open for Gmail authentication. This only happens once — subsequent runs use the saved `token.json`.
- Research quality depends on the contact's public web presence. For early-stage founders with limited coverage, the system falls back to internal notes for personalization.
- All logs are printed to the terminal where uvicorn is running.
