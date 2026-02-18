
#Autovalidation with pydantic
from pydantic import BaseModel

class OutreachRequest(BaseModel):
    first_name: str
    last_name: str
    company: str
    team_member: str

class OutreachResponse(BaseModel):
    status: str
    sent_to: str                # team member's email address
    contact_name: str           # full name of the target contact
    email_preview: str          # the generated email body