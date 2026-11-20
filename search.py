import os
import json
from dotenv import load_dotenv
from google import genai

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
def search(question, k=4):
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

# 4. 직접 질문해 보기
while True:
    question = input("\n질문 (끝내려면 엔터): ")
    if not question:
        break
    for score, text in search(question):
        print(f"{score:.3f}  {text}")