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
        payload = {
            "state": "6", # 6 is the integer state code for 'Resolved' in ServiceNow
            "close_code": "Solution provided",
            "close_notes": message,
            "comments": message 
        }
    elif decision == "ask":
        payload = {
            "comments": message 
        }
    elif decision == "escalate":
        payload = {
            "work_notes": f"Escalated by AI: {message}" 
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