import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SN_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SN_USER = os.getenv("SERVICENOW_USERNAME")
SN_PASS = os.getenv("SERVICENOW_PASSWORD")

def update_incident(sys_id: str, decision: str, message: str):
    # The exact REST API endpoint for updating a specific incident record
    endpoint = f"{SN_URL}/api/now/table/incident/{sys_id}"
    
    payload = {}
    
    # Map the decision to the specific ServiceNow table fields
    if decision == "respond":
        # Mentor Requirement: Move ticket to Resolved (State 6)
        payload = {
            "state": "6", 
            "close_code": "Software", # Required by ServiceNow to close a ticket
            "close_notes": message,
            "comments": f"AI Resolution:\n{message}"
        }
    elif decision == "ask":
        # Mentor Requirement: Leave open (do not send state), just add comment
        payload = {
            "comments": message 
        }
    elif decision == "escalate":
        # Leave open, add internal work note for human agents
        payload = {
            "work_notes": f"Escalated by AI:\n{message}" 
        }
        
   # Send the PATCH request to update the ticket
    response = httpx.patch(
        endpoint,
        auth=(SN_USER, SN_PASS),
        json=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"}
    )
    
    response.raise_for_status()
    
    # Safely try to parse the JSON, but don't crash if ServiceNow sends nothing
    try:
        return response.json()
    except Exception:
        return {"status": "success", "raw_response": response.text}