# Validates and enriches raw research results using an LLM
# Filters with internal notes to remove irrelevant or incorrect information

import os
import logging
import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ResearchValidatorService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables.")


    def validate(self, research: dict, notes: str, full_name: str, company: str) -> dict:
        logger.info(f"Validating research for {full_name} at {company}")

        return {
        "contact_name": full_name,
        "company": company,
        "validated_person": self._validate_section(
            content=research.get("person_context", ""),
            section_type="person background, role and previous employers and education",
            full_name=full_name,
            company=company,
            notes=notes
        ),
        "validated_activity": self._validate_section(
            content=research.get("activity_context", ""),
            section_type="recent public activity, interviews, publications and social media presence",
            full_name=full_name,
            company=company,
            notes=notes
        ),
        "validated_company": self._validate_section(
            content=research.get("company_context", ""),
            section_type="company news, funding and product updates",
            full_name=full_name,
            company=company,
            notes=notes
        )
    }
    

    def _validate_section(self, content: str, section_type: str,
                           full_name: str, company: str, notes: str = "") -> str:
        
        if not content.strip():
            return "No information found."
        
        notes_block = f"""
        INTERNAL NOTES (use as verification signals such as stage, location, 
        funding, previous employers etc.):
        {notes}
        """ if notes else ""
        
        prompt = f"""
        You are a research assistant validating web research results about a specific person and company/startup.
        GOAL: Filter this research to keep only content that genuinely refers to 
        {full_name} at {company}. Return a clean summary useful for a cold outreach email.
        
        CONTACT: {full_name} at {company}

        SECTION TYPE: {section_type}
        RAW RESEARCH:
        {content}

        TASK:
        1. Read through all the research carefully
        2. Keep only content that is genuinely about {full_name} at {company}
        3. Discard anything about different people with similar names or 
           unrelated companies with similar names, but be careful not to discard relevant information
           that may be phrased in a way that doesn't include the full name or company name in every sentence. Use your judgment to determine relevance based on the content.
        4. From what remains, extract the most useful facts for a cold outreach email:
           - Their current role and background
           - Recent company news (funding, product launches, partnerships etc.)
           - Any notable achievements, publications, public activity etc.
        5. Return a clean, concise summary 

        If nothing in the research is genuinely about this contact, 
        respond with: "No verified information found. Utilise internal notes for context."
        
    
        Return only the relevant information. No preamble, no commentary, no markdown.
        """

        message = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )

        result = message.content[0].text.strip()
        logger.info(f"Validation {section_type} for {full_name}")
        return result
