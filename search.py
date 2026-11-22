import os
import json
from dotenv import load_dotenv
from google import genai
from datetime import datetime, timedelta

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 1. 저장해 둔 임베딩 불러오기
with open("schedule_embeddings.json", "r", encoding="utf-8") as f:
    items = json.load(f)

# 2. 1단계에서 만든 함수 그대로
def cosine_similarity(a, b):
    dot = 0
    len_a = 0
    len_b = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
        len_a += a[i] ** 2
        len_b += b[i] ** 2
    return dot / (len_a ** 0.5 * len_b ** 0.5)

# 3. 질문 → 가장 비슷한 문장 k개
def search(question, k=5):
    emb = client.models.embed_content(
        model="gemini-embedding-2",
        contents=question,
    )
    q_vec = emb.embeddings[0].values

    scored = []
    for item in items:
        score = cosine_similarity(q_vec, item["vector"])
        scored.append((score, item["text"]))

    scored.sort(reverse=True)     # 점수 높은 순으로 정렬
    return scored[:k]             # 앞에서 k개



def upcoming(days=14,now=None):
    if now is None:
        now = datetime.now()
    today = now.strftime("%Y%m%d")         # 오늘 날짜를 "20261121" 모양 문자열로
    limit = (now + timedelta(days=days)).strftime("%Y%m%d")     # 오늘 + 14일을 "20261205" 모양 문자열로

    result = []
    for item in items:
        if item["start"] <= limit and item["end"] >= today:          # 이 일정이 오늘~limit 사이에 걸치면
            result.append(item["text"])
    return result

# print(upcoming(now = datetime.strptime("20261225","%Y%m%d")))

def answer(question):
    # 1. 자료 모으기
    found = [text for score, text in search(question)]   # 점수는 빼고 문장만
    soon = upcoming()
    docs = found + soon                                       # 두 리스트를 하나로 합치기

    # 2. 프롬프트 만들기
    today = datetime.now().strftime("%Y년 %m월 %d일")
    context = "\n".join(f"- {d}" for d in docs)          # 한 줄에 하나씩

    prompt = f"""너는 근명고등학교 학사일정 안내 도우미야.
아래 [자료]에 있는 내용만 보고 답해.
[자료]에 없으면 "학사일정에서 찾을 수 없어요"라고 답해.
우리 학교에서는 중간고사를 "1차 정기시험", 기말고사를 "2차 정기시험", 체육대회를 "체육한마당"이라고 불러.
오늘은 {today}이야.

[자료]
{context}

[질문]
{question}"""

    # 3. Gemini 호출
    res = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )
    return res.text

#4. 직접 질문해 보기
if __name__ == "__main__":
    while True:
        question = input("\n질문 (끝내려면 엔터): ")
        if not question:
            break
        print(answer(question))