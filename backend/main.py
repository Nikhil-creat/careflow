import os, re, json, httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="CareFlow API")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
                   allow_methods=["*"], allow_headers=["*"])

DEPTS = {"Cardiology": r"chest|heart|palpit|bp", "Orthopedics": r"bone|fractur|knee|joint|back",
         "Pediatrics": r"child|infant|baby|kid", "Dermatology": r"skin|rash|allerg"}
DOCTORS = {"Cardiology": "Dr. Rao", "Orthopedics": "Dr. Iyer", "General Medicine": "Dr. Khan",
           "Pediatrics": "Dr. Singh", "Dermatology": "Dr. Nair"}
EMERG = re.compile(r"chest pain|can.?t breathe|unconscious|stroke|heavy bleeding|seizure|overdose", re.I)

def triage(text: str) -> dict:
    dept = next((d for d, p in DEPTS.items() if re.search(p, text, re.I)), "General Medicine")
    return {"department": dept, "doctor": DOCTORS[dept], "emergency": bool(EMERG.search(text))}

def beds() -> dict:
    return {"ICU": 4, "General": 6, "Private": 2}  # replace with a real DB query

TOOLS = [
    {"name": "triage", "description": "Route symptoms to a department and doctor.",
     "input_schema": {"type": "object", "properties": {"symptoms": {"type": "string"}}, "required": ["symptoms"]}},
    {"name": "bed_availability", "description": "Current free beds per ward.",
     "input_schema": {"type": "object", "properties": {}}},
]
SYSTEM = ("You are CareFlow's patient navigator. Use tools to route patients to the right department. "
          "Never diagnose or prescribe. For emergencies tell them to call 108 or 112. Be brief.")

def run_tool(name, args):
    return triage(args.get("symptoms", "")) if name == "triage" else beds()

class Chat(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/triage")
def triage_ep(c: Chat):
    return triage(c.message)

@app.post("/chat")
async def chat(c: Chat):
    t = triage(c.message)
    if t["emergency"]:
        return {"reply": "This may be an emergency. Call 108 or 112 now or go to the nearest ER."}
    gk = os.getenv("GROQ_API_KEY")
    if gk:
        gt = [{"type": "function", "function": {"name": x["name"], "description": x["description"], "parameters": x["input_schema"]}} for x in TOOLS]
        msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": c.message}]
        async with httpx.AsyncClient(timeout=30) as cli:
            for _ in range(4):
                r = await cli.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {gk}"},
                    json={"model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), "messages": msgs, "tools": gt, "max_tokens": 500})
                m = r.json()["choices"][0]["message"]
                if not m.get("tool_calls"):
                    return {"reply": m.get("content", "")}
                msgs.append(m)
                for t in m["tool_calls"]:
                    msgs.append({"role": "tool", "tool_call_id": t["id"],
                                 "content": str(run_tool(t["function"]["name"], json.loads(t["function"]["arguments"] or "{}")))})
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"reply": f"Suggested path: {t['department']} with {t['doctor']}. Not a diagnosis."}
    msgs = [{"role": "user", "content": c.message}]
    async with httpx.AsyncClient(timeout=30) as cli:
        for _ in range(4):  # agent loop: model plans, calls tools, observes, answers
            r = await cli.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
                json={"model": os.getenv("MODEL", "claude-sonnet-5-5"), "max_tokens": 500,
                      "system": SYSTEM, "tools": TOOLS, "messages": msgs})
            d = r.json()
            if d.get("stop_reason") != "tool_use":
                return {"reply": "".join(b.get("text", "") for b in d.get("content", []))}
            msgs.append({"role": "assistant", "content": d["content"]})
            msgs.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": b["id"], "content": str(run_tool(b["name"], b["input"]))}
                for b in d["content"] if b["type"] == "tool_use"]})
    return {"reply": "Sorry, please try again."}
