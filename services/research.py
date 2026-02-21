import httpx
import os
from dotenv import load_dotenv
import logging
import time

load_dotenv()

logger = logging.getLogger(__name__)

#-------------  Exa Configuration --------------
EXA_URL = "https://api.exa.ai/search"
EXA_TIMEOUT = 10.0
EXA_MAX_CHARACTERS = 1000
EXA_INCLUDE_HTML = False
#Web results per category and instance
EXA_PERSON_RESULTS = 5
EXA_ACTIVITY_RESULTS = 3
EXA_COMPANY_RESULTS = 6

EXA_PERSON_DOMAINS = None  # full web
EXA_ACTIVITY_DOMAINS = None
EXA_COMPANY_DOMAINS = None
#Tried selected list to ensure reputable sources, but it was too limiting and paywall plagued
'''
[   "linkedin.com", "techcrunch.com", "sifted.eu", "eu-startups.com", "tech.eu",
    "maddyness.com", "uktech.news", "elreferente.es", "startupxplore.com",
    "novafica.com", "elconfidencial.com", "cincodias.elpais.com", "crunchbase.com", "dealroom.co",
    "wired.com", "reuters.com"
]
'''
#---------------------------------------------


class ResearchService:
    


    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            raise ValueError("EXA_API_KEY is not set in environment variables.")


    #helper method that makes a single HTTP POST request to avoid repeating HTTP logic
    def _search(self, query: str, num_results: int = 3,
                 include_domains: list = None, _retry: bool = True) -> list:
        
        payload = {
            "query": query,
            "type": "neural",
            "numResults": num_results,
            "contents": {
                "text": {
                    "maxCharacters": EXA_MAX_CHARACTERS,
                    "includeHtmlTags": EXA_INCLUDE_HTML
                }
            }
        }
        if include_domains:
            payload["includeDomains"] = include_domains

        try:
            response = httpx.post(
                EXA_URL,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=EXA_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("results", [])
        
        except httpx.TimeoutException:
            logger.warning(f"Exa search timed out for query: {query}")
            raise RuntimeError(f"Exa search timed out for query: {query}")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and _retry:
                #Exa Rate limited: waits a moment and retries once
                logger.warning("Exa rate limited, retrying once")
                time.sleep(2)
                return self._search(query, num_results, include_domains, _retry=False)
            else:
                logger.error(f"Exa API error {e.response.status_code} for query: {query}")
                raise RuntimeError(f"Exa API error {e.response.status_code} for query: {query}")


    
    def research(self, first_name: str, last_name: str, company: str) -> dict:
            full_name = f"{first_name} {last_name}"

            #Who is person
            person_results = self._search(
                f'"{full_name}" "{company}"  Europe startup founder LINKEDIN education backround',
                include_domains=EXA_PERSON_DOMAINS,
                num_results=EXA_PERSON_RESULTS)
            
            # What have they said or published recently
            activity_results = self._search(
                f'"{full_name}" "{company}" interview article publication Social-media-post 2026 2025 2024',
                num_results=EXA_ACTIVITY_RESULTS,
                include_domains=EXA_ACTIVITY_DOMAINS
            )
            
            # What is happening at their company
            company_results = self._search(
                f'"{company}" Europe Spain funding news product launch partnership 2026 2025 2024',
                num_results=EXA_COMPANY_RESULTS,
                include_domains=EXA_COMPANY_DOMAINS
            )

            person_snippets = [r["text"] for r in person_results if r.get("text")]
            activity_snippets = [r["text"] for r in activity_results if r.get("text")]
            company_snippets = [r["text"] for r in company_results if r.get("text")]


            return {
                "contact_name": full_name,
                "company": company,
                "person_context": " ".join(person_snippets),
                "activity_context": " ".join(activity_snippets),
                "company_context": " ".join(company_snippets)
            }