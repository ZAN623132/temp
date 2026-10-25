import re
import requests

BASE_DIR = "http://sairiku.net/result/2026/ageo_1025/"
HTML_URL = (
    BASE_DIR + "shtml/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamListA.html"
)

headers = {"User-Agent": "Mozilla/5.0"}

print("1. HTMLソース内から .json の参照箇所を検索中...")
res_html = requests.get(HTML_URL, headers=headers)
if res_html.status_code == 200:
    json_matches = re.findall(
        r'["\']([^"\']+\.json[^"\']*)["\']', res_html.text
    )
    print(
        f"   発見した参照: {json_matches if json_matches else 'HTML内への直接記述なし'}"
    )

print("\n2. パス候補を一括テスト中...")
candidates = [
    BASE_DIR
    + "shtml/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamListA.json",
    BASE_DIR
    + "shtml/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamList.json",
    BASE_DIR + "shtml/timeraceshukei/details/1-1-0-7-1-1.json",
    BASE_DIR
    + "shtml/timeraceshukei/json/details/1-1-0-7-1-1_TimeraceTeamListA.json",
    BASE_DIR
    + "shtml/timeraceshukei/details/json/1-1-0-7-1-1_TimeraceTeamListA.json",
    BASE_DIR
    + "shtml/json/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamListA.json",
    BASE_DIR + "json/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamListA.json",
    BASE_DIR + "json/1-1-0-7-1-1_TimeraceTeamListA.json",
]

for url in candidates:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        is_json = "json" in r.headers.get(
            "Content-Type", ""
        ).lower() or r.text.strip().startswith("{")
        if r.status_code == 200 and is_json:
            print(f"  ✅ [200 OK] {url}")
        else:
            print(f"  ✕ [{r.status_code}] {url}")
    except Exception as e:
        print(f"  エラー: {url} -> {e}")
