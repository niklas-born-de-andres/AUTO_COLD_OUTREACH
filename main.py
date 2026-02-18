
from fastapi import FastAPI, HTTPException
from models import OutreachRequest, OutreachResponse
from orchestrator import OutreachOrchestrator

app = FastAPI(title="Outreach API")
orchestrator = OutreachOrchestrator()

@app.post("/generate-outreach", response_model=OutreachResponse)
async def generate_outreach(request: OutreachRequest):
   
    try:
        result = await orchestrator.run(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
