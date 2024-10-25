from fastapi import FastAPI

app = FastAPI()


@app.post("/chat")
async def chat(user_message: str, session_id: str):
    print(user_message, session_id)
    # Call orchestrator to handle the message
    return {"response": "test"}
