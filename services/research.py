import httpx
import os
from dotenv import load_dotenv

load_dotenv()


class ResearchService:
    EXA_URL = "https://api.exa.ai/search"

    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY")

    #helper method that makes a single HTTP POST request to avoid repeating HTTP logic
    def _search(self, query: str, num_results: int = 3) -> list:
        response = httpx.post(
            self.EXA_URL,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "type": "neural",
                "numResults": num_results,
                "contents": {"text": True}
            }
        )
        response.raise_for_status()
        return response.json().get("results", [])

    #Makes two research calls: one for the person and one for their company
    def research(self, first_name: str, last_name: str, company: str) -> dict:
            full_name = f"{first_name} {last_name}"

            person_results = self._search(f"{full_name} {company}")
            company_results = self._search(f"{company} recent news 2024 2025", num_results=2)

            person_snippets = [
                r["text"][:500] for r in person_results if r.get("text")
            ]
            company_snippets = [
                r["text"][:500] for r in company_results if r.get("text")
            ]

            return {
                "contact_name": full_name,
                "company": company,
                "person_context": " ".join(person_snippets),
                "company_context": " ".join(company_snippets)
            }