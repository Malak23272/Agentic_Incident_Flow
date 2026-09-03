from typing import Optional
from fastapi import FastAPI, BackgroundTasks, status
from pydantic import BaseModel
from gemini_service import evaluate_incident
from servicenow import update_incident  # <-- NEW IMPORT

app = FastAPI()
processed_incident_ids = set()

class IncidentPayload(BaseModel):
    incident_sys_id: str
    number: str
    short_description: str = ""
    description: Optional[str] = ""
    priority: Optional[str | int] = None

def process_incident_pipeline(payload: IncidentPayload):
    print(f"--- BACKGROUND TASK: TICKET {payload.number} ---")
    
    desc = payload.description or ""
    result = evaluate_incident(payload.short_description, desc)
    
    decision = result.get('decision')
    message = result.get('message')
    
    print(f"Gemini Decision: {decision}")
    print(f"Gemini Message:  {message}")
    
    # <-- NEW WRITE-BACK STEP -->
    print("Writing update back to ServiceNow...")
    try:
        update_incident(payload.incident_sys_id, decision, message)
        print("Successfully updated ticket in ServiceNow!")
    except Exception as e:
        print(f"Failed to update ServiceNow: {e}")
        
    print("--------------------------------------------------\n")

@app.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def handle_incident(payload: IncidentPayload, background_tasks: BackgroundTasks):
    if payload.incident_sys_id in processed_incident_ids:
        print(f"Duplicate ticket ignored: {payload.number}")
        return {"status": "ignored", "reason": "already processed"}

    processed_incident_ids.add(payload.incident_sys_id)
    background_tasks.add_task(process_incident_pipeline, payload)
    return {"status": "accepted", "sys_id": payload.incident_sys_id}