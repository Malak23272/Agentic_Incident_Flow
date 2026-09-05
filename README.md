# Agentic Incident Flow: AI-Powered ServiceNow Triage

## Project Overview
This project is an automated, closed-loop incident management pipeline developed for the BARQ Systems AI Engineering Internship. It acts as an intelligent, event-driven middleware that connects a ServiceNow Personal Developer Instance (PDI) to the Gemini LLM. 

The primary goal of this service is to eliminate manual IT helpdesk triage. When a user submits a support ticket, this system instantly intercepts the request, evaluates the issue against a strict set of predefined knowledge base (KB) articles, and automatically applies the appropriate resolution, asks for missing context, or escalates the ticket to a human agent—all without manual intervention.

# demolink :https://drive.google.com/file/d/1lx1DURZfYgcZKZ6Qo_UFgiXHpKXIXkaN/view?usp=sharing

## How It Works (The 4-Step Automation Loop)
The system operates on a seamless, asynchronous webhook architecture designed to handle tickets in real time:

1. **Ticket Creation (The Trigger):** A user submits a new IT incident on the ServiceNow platform.
2. **Event Dispatch (The Webhook):** A custom Business Rule within ServiceNow instantly detects the new ticket, packages the incident details into a structured JSON payload, and dispatches it via HTTP POST to the publicly exposed FastAPI webhook (routed securely via ngrok).
3. **AI Decision Engine (The Brain):** The Python service immediately returns an HTTP 202 Accepted status to prevent ServiceNow timeouts, then pushes the ticket to a background task. The system uses an in-memory deduplication guard to prevent double-processing. It then passes the ticket description and five rigid KB articles to the Gemini LLM, instructing it to make one of three strict decisions:
   * **Respond:** The issue matches a KB article perfectly. The AI outputs the exact resolution steps.
   * **Ask:** The issue relates to a KB article, but critical hardware/software context is missing. The AI outputs a clarifying question.
   * **Escalate:** The issue falls outside the provided KB articles and requires human intervention.
4. **Ticket Write-Back (Closing the Loop):** The Python application translates the AI's decision into a REST API `PATCH` request back to ServiceNow. It automatically updates the original ticket by marking it as "Resolved" with the solution, posting a public comment with the clarifying question, or logging an internal work note for IT staff escalation.

## Technology Stack
* **Framework:** Python 3.11+, FastAPI, Uvicorn (Asynchronous web server and background task management)
* **Data Validation:** Pydantic (Strict JSON payload typing and schema enforcement)
* **AI & Logic:** Google GenAI SDK (Gemini-3.6-flash LLM for structured JSON decision-making)
* **Integration:** HTTPX (REST API client for ServiceNow write-backs)
* **Networking:** ngrok (Secure localhost tunneling for webhook exposure)
* **Platform:** ServiceNow Developer Instance (Business Rules, Table API)

---

## Troubleshooting & Technical Challenges Overcome

During the development of this automated incident flow, several critical challenges were encountered and resolved:

### 1. Webhook Payload Validation (FastAPI 422 Error)
* **The Problem:** The FastAPI webhook rejected ServiceNow payloads with a `422 Unprocessable Content` error because ticketing systems frequently omit non-mandatory fields (sending `null` for descriptions).
* **The Solution:** Refactored the `IncidentPayload` Pydantic schema to utilize `Optional[str]` and assigned default empty string values (`""`), making the webhook resilient to malformed or incomplete incoming data.

### 2. LLM Hallucinations & Context Missing
* **The Problem:** When presented with a vague ticket, the AI improperly output `respond` and invented generic IT advice instead of outputting `ask`.
* **The Solution:** Re-engineered the system prompt with strict negative constraints. The AI was explicitly forbidden from inventing troubleshooting steps and forced to output `ask` whenever specific hardware or software context was missing.

### 3. Asynchronous Write-Back Crashes (JSON Decode Error)
* **The Problem:** The system successfully updated the ServiceNow ticket, but the Python background task crashed immediately afterward because the ServiceNow API returned an empty body that `httpx` couldn't parse as JSON.
* **The Solution:** Implemented a defensive `try/except` block around the response parsing in the REST client, allowing the system to gracefully accept the empty success response without crashing the background process.

### 4. Divergent Git Histories
* **The Problem:** Pushing the final code to GitHub resulted in a `rejected (fetch first)` error because the remote repository was initialized with a default `README.md`.
* **The Solution:** Executed a `git pull origin main --allow-unrelated-histories` command to merge the remote repository's timeline with the local code before successfully pushing the project.

## How to Run This Project Locally
1. Clone this repository.
2. Create a virtual environment and install the requirements: `pip install fastapi "uvicorn[standard]" pydantic python-dotenv google-genai httpx`
3. Copy the `.env.example` file to `.env` and fill in your Gemini and ServiceNow credentials.
4. Run the local server: `uvicorn main:app --reload`
5. Open a public tunnel to port 8000 using ngrok.
6. Update your ServiceNow Business Rule to point to the new ngrok URL.