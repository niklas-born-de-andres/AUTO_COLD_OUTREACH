import os
import json
import anthropic
import logging
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)

class EmailDraftService:

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in environment variables.")
        self.client = anthropic.Anthropic(api_key=api_key)

    def draft(self, contact: dict, research: dict, team_member: dict) -> dict:
        logger.info(f"Drafting email for {contact['first_name']} {contact['last_name']}")
        
        prompt = f"""
        You are writing a cold outreach email on behalf of {team_member['name']}, 
        who works as {team_member['role']} at Kibo Ventures. Kibo Ventures is a European tech investment firm that backs founders with bold 
        ideas. They support them beyond capital, with guidance, expertise, and 
        international connections to help them scale.

        OBJECTIVE:
        Write a cold outreach email to {contact['first_name']} {contact['last_name']} 
        at {contact['company']} to open a conversation about a potential investment 
        or partnership with Kibo Ventures.

        CONTEXT ABOUT THE CONTACT:
        {research.get('validated_person', 'No information available.')}

        RECENT ACTIVITY:
        {research.get('validated_activity', 'No information available.')}

        RECENT COMPANY NEWS:
        {research.get('validated_company', 'No information available.')}

        INTERNAL NOTES:
        Use these to personalize where natural and appropriate, 
        but do not reference them directly or make it obvious they came from internal notes. 
        Also only include information relevant to the context of the email,
        do not force including notes especially if they are arbitrary facts and are irrelevant to the proposition.
        {contact['notes']}

        MUST INCLUDE:
        - A brief, natural introduction of {team_member['name']} and their role at Kibo Ventures
        - One sentence describing what Kibo Ventures does and who they back
        - A specific reference to something real about the contact. For example a project, publication, 
          competition, or initiative they are associated with (use the research context provided)
        - If there is relevant recent company news such as a funding round, product launch, 
          or notable partnership, reference it naturally (only if applicable and specific)
        - A single, clear call to action: a short call or meeting request. ask directly for a meeting or call, e.g. 20 minutes. be direct, not vague
        - Describe specifically what the contact's company does in one sentence. use the research context to get this right, do not leave it vague
        TONE:
        - Short and professional
        - Direct and human: write like a person, not a marketing department
        - Warm but not informal

        AVOID:
        - only reference specific facts if applicable, absolutely no halucinations
        - do not add or infer investment stages not explicitly mentioned
        - Em dashes or other symbols anywhere in the email including the subject line
        - Long or convoluted sentences. One idea per sentence
        - Generic openers like "I hope this email finds you well"
        - Buzzwords like "synergy", "leverage", "ecosystem", "exciting opportunity"
        - filler words that weaken the sentence, like genuinely, really, very, quite, just
        - Flattery that feels unearned. Avoid commenting on the contact's momentum or trajectory unless you can back it with a specific fact,
          and do not evaluate it (no productive, impressive etc comments).
         Avoid sentences like "that's a meaningful milestone", state the fact and move on
        - Generic subject lines that just combine two company names. the subject should be specific and give the recipient a reason to open the email
        - Vague closing sentences like "explore whether there's a conversation worth having"


        FORMAT:
            Return a JSON object with exactly these two fields:
            {{
                "subject": "the subject line",
                "body": "the full email body including sign off"
            }}
            Return only the JSON object. No preamble, no markdown, no code blocks.
            """

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(message.content[0].text)