#주소 연결 (Controller)

from datetime import date
from fastapi import FastAPI, Header, HTTPException
from schemas import FortuneRequest, FortuneResponse
from config import INTERNAL_KEY
import llm_client

app = FastAPI()

def check_key(key: str | None):
    if key != INTERNAL_KEY:
        raise HTTPException(status_code=401, detail="허용되지 않은 요청")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/fortune", response_model=FortuneResponse)
def fortune(req: FortuneRequest, x_internal_key: str | None = Header(default=None)):
    check_key(x_internal_key)
    prompt = (
        f"생년월일이 {req.birth_date}인 사람의 {date.today()} 운세를 "
        "3문장으로 재미있게 알려줘. 건강·금전에 대한 단정적인 조언은 하지 마."
    )
    return FortuneResponse(content=llm_client.ask(prompt))