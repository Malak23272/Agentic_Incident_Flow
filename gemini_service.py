import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load the environment variables from your .env file
load_dotenv()

# Grab the key securely
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Load the 5 Knowledge Base articles from the asset pack
with open("kb_articles.json", "r") as f:
    KB_ARTICLES = json.load(f)

# The prompt instructions (Deliverable 4)
PROMPT_TEMPLATE = PROMPT_TEMPLATE = """
You are an IT support AI. You only have access to the provided Knowledge Base Articles.

Knowledge Base Articles:
{kb_articles}

Incident Ticket:
- Short Description: {short_description}
- Description: {description}

Task:
Analyze the ticket and output a pure JSON response with exactly two fields: "decision" and "message".

Rules for "decision":
- "respond": Use ONLY if a KB article matches perfectly AND the ticket contains all necessary details. Provide the exact steps from the article.
- "ask": Use if the ticket is vague (e.g., "Cannot send email" or "It just doesn't work") and lacks specific context (like which email client they are using). You MUST ask for clarifying details.
- "escalate": Use if the issue does not match the KB articles at all (e.g., leave requests, vacation, payroll).

ABSOLUTE FORBIDDEN ACTIONS:
- DO NOT invent troubleshooting steps.
- DO NOT suggest checking SMTP, port 587, or DNS unless those exact words are written in the provided KB articles.
"""

def evaluate_incident(short_description: str, description: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        kb_articles=json.dumps(KB_ARTICLES, indent=2),
        short_description=short_description,
        description=description
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)