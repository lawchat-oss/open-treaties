"""國際公約抓取 + 解析腳本

Usage:
    python fetch_treaty.py <url> <output_json> --name "公約中文名" [--encoding utf-8]

從指定 URL 抓取中文公約全文，解析為 intl-law-db 的 JSON 格式：
{
  "treaty": "公約中文名",
  "total_articles": N,
  "articles": [{"article": "一", "content": "..."}]
}

條號從 HTML 中的「第X條」pattern 自動辨識（X 為中文數字或阿拉伯數字）。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

# ─── Chinese numeral conversion ──────────────────────────────

_ARABIC_TO_CN = {
    1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
    6: "六", 7: "七", 8: "八", 9: "九", 10: "十",
    11: "十一", 12: "十二", 13: "十三", 14: "十四", 15: "十五",
    16: "十六", 17: "十七", 18: "十八", 19: "十九", 20: "二十",
    21: "二十一", 22: "二十二", 23: "二十三", 24: "二十四", 25: "二十五",
    26: "二十六", 27: "二十七", 28: "二十八", 29: "二十九", 30: "三十",
    31: "三十一", 32: "三十二", 33: "三十三", 34: "三十四", 35: "三十五",
    36: "三十六", 37: "三十七", 38: "三十八", 39: "三十九", 40: "四十",
    41: "四十一", 42: "四十二", 43: "四十三", 44: "四十四", 45: "四十五",
    46: "四十六", 47: "四十七", 48: "四十八", 49: "四十九", 50: "五十",
}

# Extend to 200 for large treaties like Geneva Conventions
for i in range(51, 201):
    tens = i // 10
    ones = i % 10
    tens_map = {5: "五十", 6: "六十", 7: "七十", 8: "八十", 9: "九十",
                10: "一百", 11: "一百一十", 12: "一百二十", 13: "一百三十",
                14: "一百四十", 15: "一百五十", 16: "一百六十", 17: "一百七十",
                18: "一百八十", 19: "一百九十", 20: "二百"}
    t = tens_map.get(tens, "")
    if ones == 0:
        _ARABIC_TO_CN[i] = t
    else:
        _ARABIC_TO_CN[i] = t + _ARABIC_TO_CN[ones]


def arabic_to_cn(n: int) -> str:
    return _ARABIC_TO_CN.get(n, str(n))


_CN_NUMS = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
    "百": 100,
}


def cn_to_arabic(s: str) -> int:
    """Convert Chinese numeral to int. Handles 一百四十三 etc."""
    s = s.strip()
    if s.isdigit():
        return int(s)
    result = temp = 0
    for c in s:
        v = _CN_NUMS.get(c)
        if v is None:
            continue
        if v == 100:
            result += (temp or 1) * 100
            temp = 0
        elif v == 10:
            result += (temp or 1) * 10
            temp = 0
        else:
            temp = v
    return result + temp


# ─── Article extraction ──────────────────────────────────────

# Matches 「第一條」「第二十三條」「第143條」etc.
_ARTICLE_PATTERN = re.compile(
    r"第\s*([一二三四五六七八九十百零○〇０\d]+)\s*條"
)


def extract_articles_from_text(text: str) -> list[dict]:
    """Split plain text into articles based on 「第X條」markers."""
    # Find all article markers and their positions
    matches = list(_ARTICLE_PATTERN.finditer(text))
    if not matches:
        return []

    articles = []
    for i, m in enumerate(matches):
        art_cn = m.group(1).strip()
        # Normalize: if Arabic digits, convert to Chinese
        if art_cn.isdigit():
            art_num = int(art_cn)
            art_cn = arabic_to_cn(art_num)

        # Content starts after "第X條" marker
        start = m.end()
        # Content ends at next article marker (or end of text)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        # Clean up content: remove leading/trailing whitespace, normalize newlines
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = content.strip()

        if content:
            articles.append({"article": art_cn, "content": content})

    return articles


def fetch_and_parse(
    url: str,
    treaty_name: str,
    encoding: str = "utf-8",
) -> dict:
    """Fetch a treaty page and parse articles."""
    print(f"Fetching: {url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    r = httpx.get(url, timeout=30, follow_redirects=True, headers=headers)
    r.encoding = encoding
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Remove script/style tags
    for tag in soup.find_all(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    # Get text content
    text = soup.get_text("\n", strip=False)

    # Parse articles
    articles = extract_articles_from_text(text)

    result = {
        "treaty": treaty_name,
        "total_articles": len(articles),
        "articles": articles,
    }
    return result


def save_treaty(data: dict, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved: {output_path} ({data['total_articles']} articles)")


# ─── Batch processing ────────────────────────────────────────

# Known treaty sources (url, filename, Chinese name, expected_article_count)
TREATIES = [
    # Tier 1 — 人權公約 (OHCHR)
    {
        "key": "udhr",
        "name": "世界人權宣言",
        "url": "https://www.un.org/zh/about-us/universal-declaration-of-human-rights",
        "expected": 30,
    },
    {
        "key": "crc",
        "name": "兒童權利公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-rights-child",
        "expected": 54,
    },
    {
        "key": "cedaw",
        "name": "消除對婦女一切形式歧視公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-elimination-all-forms-discrimination-against-women",
        "expected": 30,
    },
    {
        "key": "crpd",
        "name": "身心障礙者權利公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-rights-persons-disabilities",
        "expected": 50,
    },
    {
        "key": "cat",
        "name": "禁止酷刑和其他殘忍、不人道或有辱人格的待遇或處罰公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-against-torture-and-other-cruel-inhuman-or-degrading",
        "expected": 33,
    },
    {
        "key": "genocide",
        "name": "防止及懲治滅絕種族罪公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-prevention-and-punishment-crime-genocide",
        "expected": 19,
    },
    {
        "key": "refugee",
        "name": "關於難民地位的公約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/convention-relating-status-refugees",
        "expected": 46,
    },
    # Tier 2 — 外交/領事
    {
        "key": "vcdr",
        "name": "維也納外交關係公約",
        "url": "",  # 待確認
        "expected": 53,
    },
    {
        "key": "vccr",
        "name": "維也納領事關係公約",
        "url": "",  # 待確認
        "expected": 79,
    },
    # ICCPR Optional Protocols
    {
        "key": "iccpr-op1",
        "name": "公民與政治權利國際公約任擇議定書",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/optional-protocol-international-covenant-civil-and-political",
        "expected": 14,
    },
    {
        "key": "iccpr-op2",
        "name": "旨在廢除死刑的公民與政治權利國際公約第二項任擇議定書",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/second-optional-protocol-international-covenant-civil-and",
        "expected": 11,
    },
    # Tier 4 — 太空法
    {
        "key": "outer-space",
        "name": "關於各國探索和利用外層空間包括月球與其他天體活動所應遵守原則之條約",
        "url": "https://www.ohchr.org/zh/instruments-mechanisms/instruments/treaty-principles-governing-activities-states-exploration-and",
        "expected": 17,
    },
]


def process_batch(keys: list[str] | None = None) -> dict[str, str]:
    """Process a batch of treaties. Returns {key: status}."""
    results = {}
    data_dir = Path(__file__).resolve().parent.parent / "data"
    for t in TREATIES:
        if keys and t["key"] not in keys:
            continue
        if not t["url"]:
            results[t["key"]] = "SKIP (no URL)"
            continue
        output = data_dir / f"{t['key']}.json"
        if output.exists():
            results[t["key"]] = f"EXISTS ({output.name})"
            continue
        try:
            data = fetch_and_parse(t["url"], t["name"])
            actual = data["total_articles"]
            expected = t["expected"]
            if actual < expected * 0.5:
                results[t["key"]] = f"WARN: only {actual}/{expected} articles parsed"
                # Still save for inspection
            else:
                results[t["key"]] = f"OK: {actual} articles"
            save_treaty(data, str(output))
        except Exception as e:
            results[t["key"]] = f"ERROR: {type(e).__name__}: {e}"
    return results


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        # Single treaty mode: python fetch_treaty.py <url> <output> --name "..."
        url = sys.argv[1]
        output = sys.argv[2]
        name = "Unknown"
        for i, a in enumerate(sys.argv):
            if a == "--name" and i + 1 < len(sys.argv):
                name = sys.argv[i + 1]
        data = fetch_and_parse(url, name)
        save_treaty(data, output)
    else:
        # Batch mode: process all
        print("Processing all treaties...")
        results = process_batch()
        for key, status in results.items():
            print(f"  {key}: {status}")
