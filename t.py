import json
import os
import time
from datetime import datetime, timedelta, timezone
import requests

# -------------------------------------------------------------------
# 設定エリア
# -------------------------------------------------------------------

# 確認対象ページ一覧 (手動作成した target2026.txt)
URL_FILE = "target2026.txt"

# 巡回インターバル（秒）
CHECK_INTERVAL = 10

# GitHub Gist 設定
GIST_ID = "YOUR_GIST_ID"
GIST_TOKEN = "YOUR_GIST_TOKEN"

# 確認する学校・所属の略称
TARGET_KEYWORD = "電気通信大"

# 日本時間（JST = UTC+9）の定義
JST = timezone(timedelta(hours=9))

# DoS攻撃判定回避用のHEADER設定
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    )
}

# 過去データを記録する辞書
history_data = {}

# -------------------------------------------------------------------


def load_urls():
    """target2026.txt からURL一覧を読み込む"""
    if os.path.exists(URL_FILE):
        urls = []
        with open(URL_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
        if urls:
            return urls
    return []


def gist_send(payload_data):
    """Gist API に PATCH リクエストを送り results.json を更新する"""
    gist_url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"Bearer {GIST_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    body = {
        "files": {
            "results.json": {
                "content": json.dumps(
                    payload_data, ensure_ascii=False, indent=2
                )
            }
        }
    }

    try:
        res = requests.patch(gist_url, headers=headers, json=body, timeout=10)
        if res.status_code == 200:
            print(" ✅ Gist へのデータ送信に成功しました！")
        else:
            print(f" ❌ Gist 送信エラー: {res.status_code} - {res.text}")
    except Exception as e:
        print(f" ❌ Gist 通信失敗: {e}")


def parse_race_json(data, target_keyword=TARGET_KEYWORD):
    """個別種目・集計ページのキー構造の差を自動吸収して対象校データを抽出する"""
    # タイトルの取得（優先順: SubTitle -> Title -> EventName -> RaceName）
    race_title = (
        data.get("SubTitle")
        or data.get("Title")
        or data.get("EventName")
        or data.get("RaceName")
        or "競技結果"
    )

    results = []
    seen_keys = set()
    raw_runners = []

    # 1. データ構造の判定と抽出
    if "TimeraceTeamList" in data:
        # 集計ページ構造
        raw_runners = data.get("TimeraceTeamList", [])
    elif "ResultInfo" in data:
        # 個別種目ページ構造
        result_info = data.get("ResultInfo", {})
        if isinstance(result_info, dict):
            for group in result_info.values():
                if isinstance(group, list):
                    for sub in group:
                        raw_runners.extend(sub.get("ResultList", []))

    # 2. 対象キーワートによるフィルタリングと正規化
    for r in raw_runners:
        shozoku = r.get("Shozoku") or r.get("ShozokuMei") or ""
        if target_keyword in shozoku:
