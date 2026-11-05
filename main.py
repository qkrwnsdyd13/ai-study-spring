#주소 연결 (Controller)

from datetime import date
from fastapi import FastAPI, Header, HTTPException
from schemas import FortuneRequest, FortuneResponse
from config import INTERNAL_KEY
import llm_client
from google.genai import errors

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
        "생년월일과 날짜는 답변에 쓰지 말고, 첫 문장부터 바로 운세 내용으로 시작해."
        "HTML 태그는 쓰지 말고, 문장마다 줄을 바꿔서(엔터) 써 줘."
    )
    try:
        return FortuneResponse(content=llm_client.ask(prompt))
    except errors.APIError as e:
        print("AI 호출 실패1:", e)
        if e.code == 503:      # Gemini: high demand
            raise HTTPException(status_code=503, detail="AI_BUSY")
        raise HTTPException(status_code=502, detail="AI_ERROR")
    except Exception:
        raise HTTPException(status_code=502, detail="AI_ERROR")