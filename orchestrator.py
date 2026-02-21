#sequences the full outreach pipeline
#Steps are run in thread pool to avoid blocking

import asyncio
import httpx
import logging
from services.contact_resolver import ContactResolver
from services.research import ResearchService
from services.email_drafter import EmailDraftService
from services.email_delivery import EmailDeliveryService
from models import OutreachRequest, OutreachResponse
from services.research_validator import ResearchValidatorService

logger = logging.getLogger(__name__)

class OutreachOrchestrator:
    def __init__(self):
        self.resolver = ContactResolver()
        self.researcher = ResearchService()
        self.validator = ResearchValidatorService()
        self.drafter = EmailDraftService()
        self.gmail = EmailDeliveryService()

    async def run(self, request: OutreachRequest) -> OutreachResponse:
        # Validate contact and team member exist
        contact = self.resolver.get_contact(request.first_name, request.last_name)
        team_member = self.resolver.get_team_member(request.team_member)

        #  Research the contact 
        raw_research = await asyncio.to_thread(
            self.researcher.research,
            first_name=contact["first_name"],
            last_name=contact["last_name"],
            company=contact["company"]
        )
        #validate research
        validated_research = await asyncio.to_thread(
            self.validator.validate,
            research=raw_research,
            notes=contact["notes"],
            full_name=f"{contact['first_name']} {contact['last_name']}",
            company=contact["company"]
        )

        #  Draft the email 
        draft = await asyncio.to_thread(
            self.drafter.draft,
            contact=contact,
            research=validated_research,
            team_member=team_member
        )

        # Deliver to team member's inbox 
        delivery = await asyncio.to_thread(
            self.gmail.send,
            to_email=team_member["email"],
            subject=draft["subject"],
            body=draft["body"]
        )

        # Return confirmation
        return OutreachResponse(
            status=delivery["status"],
            sent_to=team_member["email"],
            contact_name=f"{contact['first_name']} {contact['last_name']}",
            email_preview=draft["body"]
        )