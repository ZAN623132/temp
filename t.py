import json
import requests

URL = "http://sairiku.net/result/2026/ageo_1025/shtml/timeraceshukei/details/1-1-0-7-1-1_TimeraceTeamListA.json"
TARGET_KEYWORD = "電気通信大"

res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
res.encoding = "utf-8"

data = res.json()

# 個別種目ページとタイムレース集計ページの構造差を吸収
runners = []
if "TimeraceTeamList" in data:
    # 集計ページ構造
    runners = data.get("TimeraceTeamList", [])
elif "ResultInfo" in data:
    # 個別ページ構造
    result_info = data.get("ResultInfo", {})
    if isinstance(result_info, dict):
        for group in result_info.values():
            if isinstance(group, list):
                for sub in group:
                    runners.extend(sub.get("ResultList", []))

hit_count = 0
print(f"■ JSON取得成功 (全データ数: {len(runners)}件)")
print("=" * 60)

for r in runners:
    # キー名の違い（Shozoku vs ShozokuMei / Kyogisha vs KyogishaMei）を吸収
    shozoku = r.get("Shozoku") or r.get("ShozokuMei") or ""
    if TARGET_KEYWORD in shozoku:
        hit_count += 1
        name = (
            (r.get("Kyogisha") or r.get("KyogishaMei") or "")
            .replace("<br/>", " ")
            .strip()
        )
        shozoku_clean = shozoku.replace("<br/>", " ").strip()
        rank = r.get("Jyuni", "")
        record = r.get("Kiroku", "")
        bib = r.get("No", "")

        print(
            f"【発見】 総合順位:{rank}位 | No:{bib} | 氏名:{name} | 所属:{shozoku_clean} | 記録:{record}"
        )

print("=" * 60)
print(f"■ 抽出結果: 合計 {hit_count} 件")
