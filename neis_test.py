import os
import json
import time
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

params = {
    "KEY": os.getenv("NEIS_API_KEY"),
    "Type": "json",
    "pIndex": 1,
    "pSize": 1000,
    "ATPT_OFCDC_SC_CODE": "J10",
    "SD_SCHUL_CODE": "7531381",
    "AA_FROM_YMD": "20260301",
    "AA_TO_YMD": "20270228",
}

res = requests.get("https://open.neis.go.kr/hub/SchoolSchedule", params=params)
data = res.json()
rows = data["SchoolSchedule"][1]["row"]

SKIP = ["토요휴업일"]

filtered = []
for r in rows:
    if r["EVENT_NM"] not in SKIP:
        filtered.append(r)

# 합치기: 원래 코드로 되돌림 (문장은 여기서 만들지 않음)
merged = []
for r in filtered:
    if merged and merged[-1]["name"] == r["EVENT_NM"]:
        merged[-1]["end"] = r["AA_YMD"]
    else:
        merged.append({
            "name": r["EVENT_NM"],
            "start": r["AA_YMD"],
            "end": r["AA_YMD"],
            "content": r["EVENT_CNTNT"],
        })

def to_date_text(ymd):
    return f"{ymd[0:4]}년 {int(ymd[4:6])}월 {int(ymd[6:8])}일"

def group_to_sentence(g):
    if g["start"] == g["end"]:
        when = to_date_text(g["start"])
    else:
        when = to_date_text(g["start"]) + " ~ " + to_date_text(g["end"])

    sentence = f"{when}: {g['name']}"
    if g["content"] and g["content"] != g["name"]:
        sentence += f" ({g['content']})"
    return sentence

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

items = []
for i, g in enumerate(merged):            # 바뀜: 번호 i와 그룹 g 두 개만 받음
    text = group_to_sentence(g)           # 바뀜: 반복문 안에서 문장 만들기

    emb = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,                    # 바뀜: 만든 문장을 임베딩
    )
    items.append({
        "start": g["start"],              # 추가: 시작 날짜 "20261231"
        "end": g["end"],                  # 추가: 끝 날짜 "20270205"
        "text": text,
        "vector": emb.embeddings[0].values,
    })
    print(f"{i + 1}/{len(merged)} 완료")  # 바뀜: sentences 대신 merged 개수
    time.sleep(1)

with open("schedule_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False)

print("저장 완료:", len(items), "개")