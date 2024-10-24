from fastapi import FastAPI
from tomo.orchestrator import Orchestrator

app = FastAPI()

orchestrator = Orchestrator()


@app.post("/chat")
async def chat(user_message: str, session_id: str):
    # Call orchestrator to handle the message
    response = orchestrator.handle_message(user_message, session_id)
    return {"response": response}
