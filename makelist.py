import time
import urllib.parse
from bs4 import BeautifulSoup
import requests

# -------------------------------------------------------------------
# 設定エリア
# -------------------------------------------------------------------
TIMETABLE_URL = (
    "http://sairiku.net/result/2026/ageo_1025/shtml/TimeTable.html"
)

# サイト上の正確な表記（例: "〇〇高", "〇〇大", "〇〇AC"）
TARGET_KEYWORD = "電気通信大"

OUTPUT_FILE = "target2026.txt"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    )
}
# -------------------------------------------------------------------


def make_target_list():
    print(f"[{TIMETABLE_URL}] を読み込んでいます...")

    try:
        res = requests.get(TIMETABLE_URL, headers=HEADERS, timeout=5)
        # Shift_JIS (CP932) でデコード
        html_text = res.content.decode("cp932", errors="replace")
        soup = BeautifulSoup(html_text, "html.parser")

        all_links = soup.find_all("a", href=True)
        print(f"📊 ページ内総リンク数: {len(all_links)} 件")

        # 巡回対象のURLリストを抽出
        candidate_urls = []
        for a in all_links:
            href = a["href"].strip()

            # 無効なリンクやタイムテーブル自身を除外
            if (
                href.startswith("javascript:")
                or href.startswith("#")
                or "TimeTable" in href
            ):
                continue

            # 絶対URL化し、末尾のアンカー(#区分)を除去
            abs_url = urllib.parse.urljoin(TIMETABLE_URL, href)
            clean_url = abs_url.split("#")[0]

            if clean_url not in candidate_urls and clean_url != TIMETABLE_URL:
                candidate_urls.append(clean_url)

        print(f"🔍 検証対象の候補URL数: {len(candidate_urls)} 件\n")

        matched_items = []
        for index, url in enumerate(candidate_urls, 1):
            try:
                sub_res = requests.get(url, headers=HEADERS, timeout=3)
                sub_html = sub_res.content.decode("cp932", errors="replace")

                # 指定した学校名が含まれているか確認
                if TARGET_KEYWORD in sub_html:
                    sub_soup = BeautifulSoup(sub_html, "html.parser")
                    race_title = (
                        sub_soup.title.text.strip()
                        if sub_soup.title
                        else "タイトル不明"
                    )
                    matched_items.append((url, race_title))
                    print(
                        f"  ✅ [{index}/{len(candidate_urls)}] ヒット: {race_title}"
                    )
                else:
                    print(
                        f"  ✕ [{index}/{len(candidate_urls)}] 対象校なし"
                    )

            except Exception as e:
                print(f"  ⚠️ [{index}/{len(candidate_urls)}] エラー: {e}")

            time.sleep(0.1)

        # target2026.txt に保存
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
        print(f"❌ 取得エラー: {e}")


if __name__ == "__main__":
    make_target_list()
