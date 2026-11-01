#요청·응답 형태 (DTO)

from datetime import date
from pydantic import BaseModel

class FortuneRequest(BaseModel):
    birth_date: date          # "2008-06-28" 형식이 아니면 자동으로 422 에러

class FortuneResponse(BaseModel):
    content: str