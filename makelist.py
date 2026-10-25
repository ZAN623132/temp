import urllib.parse
from bs4 import BeautifulSoup
import requests

# -------------------------------------------------------------------
# 設定エリア
# -------------------------------------------------------------------
# 大会の TimeTable.html のURL
TIMETABLE_URL = (
    "http://sairiku.net/result/2026/ageo_1025/shtml/TimeTable.html"
)

# 対象学校の略称（例: "〇〇高", "〇〇大"）
TARGET_KEYWORD = "電気通信大"

OUTPUT_FILE = "target2026.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    )
}
# -------------------------------------------------------------------


def make_target_list_from_timetable():
    print(f"[{TIMETABLE_URL}] を読み込んでいます...")

    try:
        res = requests.get(TIMETABLE_URL, headers=HEADERS, timeout=5)
        res.encoding = "cp932"  # Shift_JIS/CP932
        soup = BeautifulSoup(res.text, "html.parser")

        # タイムテーブル上のすべてのリンクを取得
        links = soup.find_all("a", href=True)
        matched_items = []
        visited_urls = set()

        for a in links:
            href = a["href"]
            # 相対パスを絶対URLに変換
            abs_url = urllib.parse.urljoin(TIMETABLE_URL, href)

            # TimeTable自身や重複URLをスキップ
            if abs_url == TIMETABLE_URL or abs_url in visited_urls:
                continue

            visited_urls.add(abs_url)

            # リンク先のページを開いて自校の選手がいるか判定
            try:
                sub_res = requests.get(abs_url, headers=HEADERS, timeout=3)
                sub_res.encoding = "cp932"

                if TARGET_KEYWORD in sub_res.text:
                    sub_soup = BeautifulSoup(sub_res.text, "html.parser")
                    race_title = (
                        sub_soup.title.text.strip()
                        if sub_soup.title
                        else a.get_text(strip=True)
                    )
                    matched_items.append((abs_url, race_title))
                    print(f"✅ ヒット: {race_title} ({abs_url})")

            except Exception as e:
                print(f"⚠️ リンク先取得エラー ({abs_url}): {e}")

        # 結果を target2026.txt に保存
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(
                f"# '{TARGET_KEYWORD}' 出場種目リスト"
                f" (全{len(matched_items)}件)\n\n"
            )
            for url, title in matched_items:
                f.write(f"# {title}\n")
                f.write(f"{url}\n\n")

        print(
            f"\n🎉 完了！ {len(matched_items)} 件の対象URLを"
            f" '{OUTPUT_FILE}' に保存しました。"
        )

    except Exception as e:
        print(f"❌ TimeTableの取得失敗: {e}")


if __name__ == "__main__":
    make_target_list_from_timetable()
