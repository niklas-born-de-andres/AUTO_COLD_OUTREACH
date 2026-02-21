import logging
from fastapi import FastAPI, HTTPException
from models import OutreachRequest, OutreachResponse
from orchestrator import OutreachOrchestrator

#Logging for error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kibo Outreach API")
orchestrator = OutreachOrchestrator()

@app.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach(request: OutreachRequest):
   
    try:
        result = await orchestrator.run(request)
        logger.info(f"Email successfully delivered to {result.sent_to}")
        return result
    except ValueError as e:
        # Contact or team member not found in CSVs
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        #Unexpected error. full details are logged server side
        logger.error(f"Unexpected error processing request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
