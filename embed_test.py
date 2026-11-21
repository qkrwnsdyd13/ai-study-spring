import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

sentences = [
    "기말고사는 12월 둘째 주에 시작한다.",
    "중간고사는 10월에 끝났다.",
    #"2학기 시험 일정이 언제야?",
    "2학기 기말고사가 몇 월 며칠부터 시작하는지 알려줘",
    "오늘 급식 메뉴는 짜장면이다.",
]

result = client.models.embed_content(
    model="gemini-embedding-2",
    contents=sentences,          # 리스트로 여러 문장을 한 번에 보낼 수 있어요
)

vectors = []
for s in sentences:
    r = client.models.embed_content(
        model="gemini-embedding-2",
        contents=s,             # 문장 하나
    )
    vectors.append(r.embeddings[0].values)

a = vectors[0]  # 첫 문장 → 숫자 리스트
b = vectors[1]   # 두 번째 문장

# print(len(a))      # 숫자가 몇 개인지
# print(a[:5])       # 앞 5개만 보기
# print(b[:5])       # 앞 5개만 보기

def cosine_similarity(a, b):
    dot = 0        # ① 내적을 모을 변수
    len_a = 0      # ② a의 제곱합
    len_b = 0      # ② b의 제곱합

    for i in range(len(a)):       # 0번부터 마지막 번호까지
        dot += a[i] * b[i]        # 같은 위치끼리 곱해서 더하기
        len_a += a[i] ** 2        # a의 각 값 제곱해서 더하기
        len_b += b[i] ** 2        # b의 각 값 제곱해서 더하기

    len_a = len_a ** 0.5          # 루트 (0.5제곱 = 루트)
    len_b = len_b ** 0.5

    return dot / (len_a * len_b)  # ③ 나누기

print(cosine_similarity(vectors[1], vectors[2]))