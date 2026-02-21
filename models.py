
#Autovalidation with pydantic
from pydantic import BaseModel, field_validator

class OutreachRequest(BaseModel):
    first_name: str
    last_name: str
    company: str
    team_member: str

    @field_validator("*", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        # Trim accidental leading/trailing spaces from all fields
        if isinstance(v, str):
            return v.strip()
        return v

class OutreachResponse(BaseModel):
    status: str
    sent_to: str                
    contact_name: str           
    email_preview: str         