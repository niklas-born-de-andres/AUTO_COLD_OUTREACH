# ConnectionStrategyService: generates a personalized connection strategy for a contact.
# Runs additional Exa searches for events and published content, then uses Claude Sonnet
# to generate a second email to the team member with concrete relationship-building angles.

import os
import logging
import anthropic
from dotenv import load_dotenv
from services.research import ResearchService

load_dotenv()

logger = logging.getLogger(__name__)

class ConnectionStrategyService:

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables.")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.researcher = ResearchService()


    def generate(self, contact: dict, research: dict, team_member: dict) -> dict:

        full_name = f"{contact['first_name']} {contact['last_name']}"
        company = contact["company"]
        logger.info(f"Generating connection strategy for {full_name} at {company}")

        # Additional targeted searches
        strategy_research = self.researcher.research_strategy(full_name, company)
        
        prompt = f"""
        You are a relationship strategist helping {team_member['name']} at Kibo Ventures 
        build a connection with {full_name}, Co-Founder of {company}.

        GOAL: Write a concise, actionable connection strategy that {team_member['name']} 
        can use to warm up the relationship before or after the initial outreach.

        VALIDATED RESEARCH:
        {research.get('validated_person', '')}
        {research.get('validated_company', '')}

        INTERNAL NOTES:
        {contact['notes']}

        EVENTS RESEARCH:
        {strategy_research.get('events_context', 'No specific events found.')}

        PUBLISHED CONTENT RESEARCH:
        {strategy_research.get('content_context', 'No specific content found.')}
        
        STRUCTURE:
        Write a short internal strategy note. No headers with lines, no manual, no sequence narrative.
        Use these sections only if you have something specific and actionable to say — skip any section 
        where you would be vague or generic:

        WARM INTRODUCTION ANGLES
        Short bullets. Specific ecosystem overlaps, shared accelerators, mutual network paths.

        UPCOMING EVENTS  
        Short bullets. Specific events relevant to their stage, industry, and geography.

        CONTENT HOOKS
        Short bullets. Specific posts, milestones, or announcements worth engaging with directly.

        COMMUNITY PLAY: Identify a specific LinkedIn post, thread, or community 
        where the contact is active and suggest a genuine way to engage before direct outreach

        ALTERNATIVE CHANNELS
        Short bullets. Any verified social media, newsletters, podcasts, or communities 
        where the contact is active. If none found, skip this section entirely.

        INDUSTRY REPORTS
        Short bullets. Any relevant industry reports, new regulations, trends, or breakthroughs related to the contact's company.
        Statistics relevant to the contact's company or industry that could be useful conversation starters.

        RECOMMENDED NEXT STEPS
        3 to 5 short bullets. Concrete options ranked by ease, not a sequence, just options 
        {team_member['name']} can choose from.

        TONE:
        - Internal note — direct and practical
        - Specific over generic
        - No lines or dividers between sections
        - No closing sign-off

        AVOID:
        - Generic advice that applies to any founder
        - Sections with no specific, actionable content
        - Em dashes
        - Writing a manual or narrative
        - Including sections without specific content (e.g. if no relevant events are found, skip the "Upcoming Events" section entirely)

        FORMAT:
        Return a JSON object with exactly these two fields:
        {{
            "subject": "Connection strategy — {full_name} / {company}",
            "body": "the full strategy email body"
        }}
        Return only the JSON object. No preamble, no markdown, no code blocks.
        """

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )

        try:
            import json
            raw = message.content[0].text
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)
            logger.info(f"Connection strategy generated for {full_name}")
            return result
        except json.JSONDecodeError:
            logger.error("Connection strategy returned invalid JSON")
            raise RuntimeError("Connection strategy failed to return valid JSON.")