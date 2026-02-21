# Unused die to poor results and timeout errors

import httpx
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- Cala Configuration ---
CALA_BASE_URL = "https://api.cala.ai/v1/knowledge"
CALA_TIMEOUT = 100.0
# --------------------------

class ResearchService:
    def __init__(self):
        self.api_key = os.getenv("CALA_API_KEY")
        if not self.api_key:
            raise ValueError("CALA_API_KEY is not set in environment variables.")
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    # Find entity by name and return the top match
    def _entity_search(self, name: str, entity_type: str = "PERSON") -> dict | None:
        try:
            response = httpx.get(
                f"{CALA_BASE_URL}/entities",
                headers=self.headers,
                params={"name": name, "entity_types": entity_type, "limit": 1},
                timeout=CALA_TIMEOUT
            )
            response.raise_for_status()
            entities = response.json().get("entities", [])
            return entities[0] if entities else None

        except httpx.TimeoutException:
            raise RuntimeError(f"Cala entity search timed out for: {name}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Cala API error {e.response.status_code} for entity search: {name}")

    # Get full profile for a known entity ID
    def _get_entity(self, entity_id: int) -> dict:
        try:
            response = httpx.get(
                f"{CALA_BASE_URL}/entities/{entity_id}",
                headers=self.headers,
                timeout=CALA_TIMEOUT
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            raise RuntimeError(f"Cala get entity timed out for ID: {entity_id}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Cala API error {e.response.status_code} for entity ID: {entity_id}")

    
    def _knowledge_search(self, query: str) -> str:
        try:
            response = httpx.post(
                f"{CALA_BASE_URL}/search",
                headers=self.headers,
                json={"input": query},
                timeout=CALA_TIMEOUT
            )
            response.raise_for_status()
            return response.json().get("content", "")

        except httpx.TimeoutException:
            raise RuntimeError(f"Cala knowledge search timed out for query: {query}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("Cala rate limited — retrying once after 2 seconds")
                time.sleep(2)
                return self._knowledge_search(query)
            raise RuntimeError(f"Cala API error {e.response.status_code} for query: {query}")

    
    def research(self, first_name: str, last_name: str, company: str) -> dict:
        full_name = f"{first_name} {last_name}"
        logger.info(f"Researching {full_name} at {company}")

        # Look up the person as a verified entity
        person_profile = {}
        entity = self._entity_search(full_name, entity_type="PERSON")
        if entity:
            try:
                person_profile = self._get_entity(entity["id"])
                logger.info(f"Found entity profile for {full_name}")
            except RuntimeError:
                logger.warning(f"Entity profile timed out for {full_name} — continuing without it")



        #  Search for recent activity and news
        activity_context = self._knowledge_search(
            f"{full_name} {company} recent activity interview publication 2024 2025"
        )

        # Search for company news
        company_context = self._knowledge_search(
            f"{company} {full_name} funding news product launch 2024 2025"
        )

        return {
            "contact_name": full_name,
            "company": company,
            "person_profile": person_profile,
            "activity_context": activity_context,
            "company_context": company_context
        }
