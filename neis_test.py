import os
import requests                      # pip install requests (venv 켜고!)
from dotenv import load_dotenv
import json

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
print(json.dumps(data, indent=2, ensure_ascii=False))       # 먼저 통째로 찍어서 구조 보기
#print(data.SchoolSchedule.EVENT_NM)
