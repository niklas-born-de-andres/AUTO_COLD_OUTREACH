# Auto Cold Outreach

An automated cold outreach pipeline to contact founders. Given a target contact and an assigned team member, the system researches the contact online, enriches the research with internal notes, drafts a personalized email using an LLM, and delivers it to the team member's Gmail inbox.

---

## Project Structure

- `main.py`  FastAPI app, exposes the single POST endpoint
- `orchestrator.py`  sequences the full pipeline from research to delivery
- `models.py`  Pydantic request and response models
- `services/contact_resolver.py`  validates contacts and team members against the CSV files
- `services/research.py`  runs three targeted Exa web searches per contact
- `services/research_validator.py`  filters raw research with Claude Haiku to avoid factual errors
- `services/email_drafter.py`  generates the personalized email with Claude Sonnet
- `services/gmail_delivery.py`  delivers the draft to the team member's Gmail inbox

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

### 5. Set up Gmail authentication

Create a Google Cloud project, enable the Gmail API, and generate an OAuth Client ID 
(Desktop app) from the Credentials page. If prompted, configure the consent screen 
first and choose External. Download the credentials file, rename it to 
`credentials.json` and place it in the project root.

On first run a browser window will open to authenticate with Google. A `token.json` 
file will be saved automatically.

---

## Running the API

```bash
uvicorn main:app --reload
```

If run locally, FastAPI provides an interactive testing UI at `http://127.0.0.1:8000/docs`

---

## Usage

```bash
curl -X POST http://127.0.0.1:8000/generate-outreach \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "string",
    "last_name": "string",
    "company": "string",
    "team_member": "string"
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



## Error Handling

| Status | Meaning |
|--------|---------|
| `200` | Email successfully generated and delivered |
| `404` | Contact or team member not found in CSV |
| `500` | Unexpected error: check terminal logs for details |

---



## Notes

- The first time the API runs, a browser window will open for Gmail authentication. This only happens once  subsequent runs use the saved `token.json`.
- Research quality depends on the contact's public web presence. For early-stage founders with limited coverage, the system might fall back to internal notes for personalization. This is part;y due to EXA's limitations. Further tools like CALA AI were tested but provided similar results.  
- All logs are printed to the terminal where uvicorn is running.
