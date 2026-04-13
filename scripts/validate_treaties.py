#!/usr/bin/env python3
"""國際法公約 JSON 品質驗證腳本"""

import json
import os
import re
import sys
from pathlib import Path
from collections import Counter

DIR = Path(__file__).resolve().parent.parent / "data"

# 用來「檢測」條文資料中是否殘留簡體中文的參考字集。
# 這些字是簡體獨有字形（例如「国」是「國」的簡體），不會出現在正確的繁體條文中。
# 若驗證報告 flag 到簡體字，代表該條文的中文翻譯來源可能是簡體版，需要人工確認。
SIMPLIFIED_CHARS = set("国个为这对关从发现实经过义体产书门问间长开动机权会级专让进种将达华号战导")

# HTML / 雜質殘留 patterns
HTML_PATTERNS = [
    (r"<div[^>]*>", "<div>"),
    (r"<span[^>]*>", "<span>"),
    (r"</div>", "</div>"),
    (r"</span>", "</span>"),
    (r"&nbsp;", "&nbsp;"),
    (r"\[編輯\]", "[編輯]"),
    (r"Copyright", "Copyright"),
    (r"版權", "版權"),
    (r"列印", "列印"),
]


def get_content(art: dict) -> str:
    """取得條文內容，支援 content 或 content_zh"""
    return art.get("content") or art.get("content_zh") or ""


def check_file(filepath: Path) -> dict:
    result = {
        "file": filepath.name,
        "json_ok": False,
        "total_declared": 0,
        "total_actual": 0,
        "count_match": False,
        "duplicates": [],
        "empty_articles": [],
        "fragment_articles": [],  # content < 10 chars
        "simplified_count": 0,
        "simplified_examples": [],
        "html_residue": [],
        "article_format": "",  # 中文數字 / 阿拉伯數字 / 混合
        "pass": False,
    }

    # 1. JSON 合法性
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["json_ok"] = True
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result["error"] = str(e)
        return result

    articles = data.get("articles", [])
    result["total_declared"] = data.get("total_articles", "N/A")
    result["total_actual"] = len(articles)

    # 2. total_articles 一致性
    result["count_match"] = result["total_declared"] == result["total_actual"]

    # 3. 無重複條號
    art_numbers = [a.get("article", "") for a in articles]
    counter = Counter(art_numbers)
    result["duplicates"] = [num for num, cnt in counter.items() if cnt > 1]

    # 4. 無空條文
    for a in articles:
        content = get_content(a)
        if not content or not content.strip():
            result["empty_articles"].append(a.get("article", "?"))

    # 5. 碎片條文 (< 10 字)
    for a in articles:
        content = get_content(a).strip()
        if content and len(content) < 10:
            result["fragment_articles"].append(
                (a.get("article", "?"), len(content), content)
            )

    # 6. 簡體字檢測
    all_text = json.dumps(data, ensure_ascii=False)
    found_simplified = []
    for ch in all_text:
        if ch in SIMPLIFIED_CHARS:
            found_simplified.append(ch)
    result["simplified_count"] = len(found_simplified)
    if found_simplified:
        # 列出每個字出現次數
        sc = Counter(found_simplified)
        result["simplified_examples"] = [
            f"{ch}x{cnt}" for ch, cnt in sc.most_common(10)
        ]

    # 7. HTML 殘留
    for pattern, label in HTML_PATTERNS:
        matches = re.findall(pattern, all_text)
        if matches:
            result["html_residue"].append(f"{label}x{len(matches)}")

    # 8. 條號格式
    has_chinese = False
    has_arabic = False
    chinese_num_pattern = re.compile(r"^[一二三四五六七八九十百零千]+$")
    arabic_num_pattern = re.compile(r"^\d+")

    for a in articles:
        art_num = str(a.get("article", ""))
        if chinese_num_pattern.match(art_num):
            has_chinese = True
        if arabic_num_pattern.match(art_num):
            has_arabic = True

    if has_chinese and has_arabic:
        result["article_format"] = "混合"
    elif has_chinese:
        result["article_format"] = "中文數字"
    elif has_arabic:
        result["article_format"] = "阿拉伯數字"
    else:
        result["article_format"] = "未知"

    # 判定：JSON OK + 數量一致 + 無重複 + 無空條文 = PASS
    # (碎片、簡體、HTML 殘留 只報告不自動 fail)
    result["pass"] = (
        result["json_ok"]
        and result["count_match"]
        and len(result["duplicates"]) == 0
        and len(result["empty_articles"]) == 0
    )

    return result


def main():
    json_files = sorted(DIR.glob("*.json"))
    if not json_files:
        print("找不到 JSON 檔案！")
        sys.exit(1)

    results = []
    for f in json_files:
        results.append(check_file(f))

    # === 表格輸出 ===
    header = "檔案名 | 條文數 | 重複 | 空條文 | 碎片(<10字) | 簡體字 | HTML殘留 | 條號格式 | 判定"
    sep = "---|---|---|---|---|---|---|---|---"
    print(header)
    print(sep)

    pass_count = 0
    for r in results:
        if not r["json_ok"]:
            print(
                f"{r['file']} | JSON ERROR | - | - | - | - | - | - | FAIL"
            )
            continue

        count_str = f"{r['total_actual']}"
        if not r["count_match"]:
            count_str += f" (宣告{r['total_declared']})"

        dup_str = ",".join(r["duplicates"]) if r["duplicates"] else "0"
        empty_str = ",".join(r["empty_articles"]) if r["empty_articles"] else "0"
        frag_str = str(len(r["fragment_articles"])) if r["fragment_articles"] else "0"
        simp_str = str(r["simplified_count"]) if r["simplified_count"] else "0"
        html_str = ", ".join(r["html_residue"]) if r["html_residue"] else "0"
        fmt_str = r["article_format"]
        verdict = "PASS" if r["pass"] else "FAIL"

        if r["pass"]:
            pass_count += 1

        print(
            f"{r['file']} | {count_str} | {dup_str} | {empty_str} | {frag_str} | {simp_str} | {html_str} | {fmt_str} | {verdict}"
        )

    print()
    print(f"=== 總結：{pass_count}/{len(results)} 通過 ===")
    print()

    # === 詳細報告 ===

    # 碎片條文詳情
    any_fragments = False
    for r in results:
        if r.get("fragment_articles"):
            if not any_fragments:
                print("--- 碎片條文詳情 (<10字) ---")
                any_fragments = True
            print(f"\n  [{r['file']}]")
            for art, length, content in r["fragment_articles"]:
                print(f"    第{art}條 ({length}字): {content}")

    # 簡體字詳情
    any_simplified = False
    for r in results:
        if r.get("simplified_count", 0) > 0:
            if not any_simplified:
                print("\n--- 簡體字詳情 ---")
                any_simplified = True
            print(f"  [{r['file']}] {r['simplified_count']}個: {', '.join(r['simplified_examples'])}")

    # HTML 殘留詳情
    any_html = False
    for r in results:
        if r.get("html_residue"):
            if not any_html:
                print("\n--- HTML 殘留詳情 ---")
                any_html = True
            print(f"  [{r['file']}] {', '.join(r['html_residue'])}")

    # 數量不一致
    any_mismatch = False
    for r in results:
        if r["json_ok"] and not r["count_match"]:
            if not any_mismatch:
                print("\n--- total_articles 不一致 ---")
                any_mismatch = True
            print(
                f"  [{r['file']}] 宣告 {r['total_declared']}, 實際 {r['total_actual']}"
            )

    # 重複條號
    any_dup = False
    for r in results:
        if r.get("duplicates"):
            if not any_dup:
                print("\n--- 重複條號 ---")
                any_dup = True
            print(f"  [{r['file']}] {', '.join(r['duplicates'])}")

    # 空條文
    any_empty = False
    for r in results:
        if r.get("empty_articles"):
            if not any_empty:
                print("\n--- 空條文 ---")
                any_empty = True
            print(f"  [{r['file']}] 第{', '.join(r['empty_articles'])}條")

    if pass_count == len(results):
        print("\n所有檔案皆通過基本品質檢查。")


if __name__ == "__main__":
    main()
