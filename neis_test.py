import os
import requests                      # pip install requests (venv 켜고!)
from dotenv import load_dotenv
import json
import time
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

#print(data)          # 먼저 통째로 찍어서 구조 보기
rows = data["SchoolSchedule"][1]["row"]

SKIP = ["토요휴업일"]          # 뺄 행사명 (필요하면 더 추가)

filtered = []
for r in rows:
    if r["EVENT_NM"] not in SKIP:
        filtered.append(r)              # 일정 전체를 넣기

merged = []
for r in filtered:
    grades = (r["ONE_GRADE_EVENT_YN"],r["TW_GRADE_EVENT_YN"],r["THREE_GRADE_EVENT_YN"])

    # 바로 앞 그룹과 행사명이 같으면 → 끝 날짜만 늘리기
    if merged and merged[-1]["name"] == r["EVENT_NM"] and merged[-1]["grades"] == grades:
        merged[-1]["end"] = r["AA_YMD"]
    # 다르면 → 새 그룹 시작 (시작 = 끝 = 오늘)
    else:
        merged.append({
            "name": r["EVENT_NM"],
            "start": r["AA_YMD"],
            "end": r["AA_YMD"],
            "content": r["EVENT_CNTNT"],
            "grades" : grades
        })

# for g in merged:
#     print(g["start"], g["end"], g["name"])

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

def grade_text(g1, g2, g3):
    grades = []
    if g1 == "Y":
        grades.append("1")
    # 2학년, 3학년도 같은 방식으로
    if g2 == "Y":
        grades.append("2")
    if g3 == "Y":
        grades.append("3")
    if grades == ["1", "2", "3"] or not grades:   # 전교생이거나, 해당 학년이 없으면
        return ""
    return " (" + ", ".join(grades) + "학년)"

# for g in merged:
#     print(group_to_sentence(g))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

   # 문장 리스트

items = []
for i, g in enumerate(merged):
    sentences = group_to_sentence(g) + grade_text(*g["grades"])

    emb = client.models.embed_content(
        model="gemini-embedding-2",
        contents=sentences,                    # 1단계와 같아요
    )
    items.append({
        "start": g["start"],
        "end": g["end"],
        "text": sentences,
        "vector": emb.embeddings[0].values,                   # 숫자 3072개 꺼내기
    })
    print(f"{i + 1}/{len(merged)} 완료")   # 진행 상황
    time.sleep(1)                             # 너무 빨리 보내지 않게 1초 쉬기

with open("schedule_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False)

print("저장 완료:", len(items), "개")