"""國際法公約查詢 MCP Server

支援 28 部國際公約、1,914 條條文的中英雙語查詢：
- 聯合國憲章、ICJ 規約、UNCLOS 海洋法公約
- ICCPR / ICESCR 兩公約 + 任擇議定書
- VCLT 條約法公約、UDHR 世界人權宣言
- 日內瓦四公約 + 兩附加議定書
- 羅馬規約、CAT、滅種公約、難民公約、外太空條約
- CEDAW、CRC、CRPD、ICERD、UNCAC、VCDR、VCCR
"""

import json
import re
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

DATA_DIR = Path(__file__).parent / "data"

# Treaty aliases for fuzzy matching
TREATY_ALIASES = {
    "un-charter": ["聯合國憲章", "UN Charter", "憲章", "联合国宪章"],
    "icj-statute": ["國際法院規約", "ICJ Statute", "ICJ規約", "ICJ", "法院規約"],
    "unclos": ["聯合國海洋法公約", "UNCLOS", "海洋法公約", "海洋法", "联合国海洋法公约"],
    "icescr": ["經濟社會文化權利國際公約", "ICESCR", "經社文公約", "經社文", "两公约", "兩公約"],
    "iccpr": ["公民與政治權利國際公約", "ICCPR", "公政公約", "公政"],
    "vclt": ["維也納條約法公約", "VCLT", "條約法公約", "維也納條約法", "Vienna Convention"],
    "op-icescr": ["經濟社會文化權利國際公約任擇議定書", "OP-ICESCR", "ICESCR任擇議定書", "Optional Protocol"],
    "udhr": ["世界人權宣言", "UDHR", "Universal Declaration of Human Rights", "人權宣言"],
    "cat": ["禁止酷刑公約", "CAT", "禁止酷刑和其他殘忍不人道或有辱人格的待遇或處罰公約", "Convention against Torture"],
    "genocide": ["防止及懲治滅絕種族罪公約", "Genocide Convention", "滅種公約", "滅絕種族罪公約"],
    "refugee": ["關於難民地位的公約", "Refugee Convention", "難民公約", "1951難民公約"],
    "rome-statute": ["國際刑事法院羅馬規約", "Rome Statute", "羅馬規約", "ICC Statute", "ICC"],
    "iccpr-op1": ["公民與政治權利國際公約任擇議定書", "ICCPR-OP1", "ICCPR第一任擇議定書", "公政公約任擇議定書"],
    "iccpr-op2": ["旨在廢除死刑的公民與政治權利國際公約第二項任擇議定書", "ICCPR-OP2", "ICCPR第二任擇議定書", "廢除死刑議定書"],
    "outer-space": ["外太空條約", "Outer Space Treaty", "OST", "關於各國探測及使用外層空間包括月球與其他天體活動所應遵守原則的條約"],
    "gc-i": ["日內瓦第一公約", "Geneva Convention I", "GC-I", "改善戰地武裝部隊傷者病者境遇之公約"],
    "gc-ii": ["日內瓦第二公約", "Geneva Convention II", "GC-II", "改善海上武裝部隊傷者病者及遇船難者境遇之公約"],
    "gc-iii": ["日內瓦第三公約", "Geneva Convention III", "GC-III", "關於戰俘待遇之公約", "戰俘公約"],
    "gc-iv": ["日內瓦第四公約", "Geneva Convention IV", "GC-IV", "關於戰時保護平民之公約", "平民保護公約"],
    "gc-ap1": ["日內瓦公約第一附加議定書", "Additional Protocol I", "AP-I", "第一附加議定書"],
    "gc-ap2": ["日內瓦公約第二附加議定書", "Additional Protocol II", "AP-II", "第二附加議定書"],
    "cedaw": ["消除對婦女一切形式歧視公約", "CEDAW", "Convention on the Elimination of All Forms of Discrimination against Women", "消除婦女歧視公約", "婦女公約"],
    "crc": ["兒童權利公約", "CRC", "Convention on the Rights of the Child", "兒童公約"],
    "crpd": ["身心障礙者權利公約", "CRPD", "Convention on the Rights of Persons with Disabilities", "身障公約", "障礙者權利公約"],
    "icerd": ["消除一切形式種族歧視國際公約", "ICERD", "International Convention on the Elimination of All Forms of Racial Discrimination", "種族歧視公約"],
    "uncac": ["聯合國反腐敗公約", "UNCAC", "United Nations Convention against Corruption", "反腐敗公約", "反貪腐公約"],
    "vcdr": ["維也納外交關係公約", "VCDR", "Vienna Convention on Diplomatic Relations", "外交關係公約"],
    "vccr": ["維也納領事關係公約", "VCCR", "Vienna Convention on Consular Relations", "領事關係公約"],
}

# Load all treaties at startup
_treaties: dict[str, dict] = {}

def _load_treaties():
    for json_file in DATA_DIR.glob("*.json"):
        key = json_file.stem
        with open(json_file, "r", encoding="utf-8") as f:
            _treaties[key] = json.load(f)

_load_treaties()


def _resolve_treaty(name: str) -> str | None:
    """Resolve a treaty name/alias to its key.

    Priority: exact key → exact alias → input contains alias → alias contains input.
    Within each tier, longer alias wins (more specific).
    """
    name_lower = name.lower().strip()
    if not name_lower:
        return None
    # 1. Exact key match
    if name_lower in TREATY_ALIASES:
        return name_lower
    # 2. Exact alias match
    for key, aliases in TREATY_ALIASES.items():
        for alias in aliases:
            if alias.lower() == name_lower:
                return key
    # 3. Input contains alias (user typed more context)
    candidates = []
    for key, aliases in TREATY_ALIASES.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in name_lower:
                candidates.append((key, len(alias)))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    # 4. Alias contains input (user typed abbreviation) — only if no tier-3 match
    candidates = []
    for key, aliases in TREATY_ALIASES.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if name_lower in alias_lower:
                # Penalize: prefer shorter alias (closer to exact match)
                candidates.append((key, -len(alias)))
    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    return None


def _cn_to_int(s: str) -> int:
    """Convert Chinese numeral string to int. Handles both 二百八十七 and 二八七 formats."""
    cn = {"零": 0, "〇": 0, "○": 0, "０": 0, "一": 1, "二": 2, "三": 3, "四": 4,
          "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10, "百": 100}
    if not s:
        return 0
    if s.isdigit():
        return int(s)
    if "百" in s or ("十" in s and len(s) <= 3):
        result = temp = 0
        for c in s:
            if c == "百":
                result += (temp or 1) * 100
                temp = 0
            elif c == "十":
                result += (temp or 1) * 10
                temp = 0
            else:
                temp = cn.get(c, 0)
        return result + temp
    else:
        digits = [cn.get(c, 0) for c in s if c in cn]
        result = 0
        for d in digits:
            result = result * 10 + d
        return result


def _normalize_article_no(s: str) -> int:
    """Normalize article number from various formats to int."""
    s = s.strip().replace("§", "").replace("第", "").replace("條", "").replace("条", "").strip()
    if s.isdigit():
        return int(s)
    return _cn_to_int(s)


mcp = FastMCP("open-treaties", instructions="查詢國際法公約條文的 MCP 工具")


@mcp.tool()
def list_treaties() -> dict:
    """列出所有可查詢的國際公約。"""
    result = []
    for key, data in _treaties.items():
        result.append({
            "key": key,
            "name": data["treaty"],
            "total_articles": data["total_articles"],
            "aliases": TREATY_ALIASES.get(key, []),
        })
    return {"treaties": result}


@mcp.tool()
def query_treaty(
    treaty_name: str,
    article_no: str = "",
    from_no: str = "",
    to_no: str = "",
) -> dict:
    """查詢國際公約條文。

    可查單條、範圍、或全文。

    Args:
        treaty_name: 公約名稱或代碼（如「UNCLOS」「海洋法公約」「ICJ」「VCLT」）
        article_no: 條號（如「38」「287」），查單一條文
        from_no: 起始條號，查範圍時使用
        to_no: 截止條號，查範圍時使用
    """
    key = _resolve_treaty(treaty_name)
    if not key:
        available = [f"{k} ({_treaties[k]['treaty']})" for k in _treaties]
        return {"success": False, "error": f"找不到「{treaty_name}」", "available": available}

    data = _treaties[key]
    articles = data["articles"]

    def _art_to_int(s: str) -> int:
        try:
            return int(s)
        except ValueError:
            return _cn_to_int(s)

    # Single article
    treaty_display = data.get("treaty_zh", data["treaty"])

    if article_no:
        target = _normalize_article_no(article_no)
        for a in articles:
            if _art_to_int(a["article"]) == target:
                return {
                    "success": True,
                    "treaty": treaty_display,
                    "article": a,
                }
        return {"success": False, "error": f"第{article_no}條不存在於{treaty_display}"}

    # Range
    if from_no or to_no:
        start = _normalize_article_no(from_no) if from_no else 1
        end = _normalize_article_no(to_no) if to_no else 9999
        matched = [a for a in articles if start <= _art_to_int(a["article"]) <= end]
        return {
            "success": True,
            "treaty": treaty_display,
            "range": f"第{start}條-第{end}條",
            "count": len(matched),
            "articles": matched,
        }

    # Full text (return first 30 articles to avoid token explosion)
    return {
        "success": True,
        "treaty": treaty_display,
        "total_articles": data["total_articles"],
        "note": "條文過多，僅顯示前30條。請用 article_no 或 from_no/to_no 查詢特定條文。",
        "articles": articles[:30],
    }


@mcp.tool()
def search_treaty(keyword: str, treaty_name: str = "") -> dict:
    """在國際公約中搜尋關鍵字。

    Args:
        keyword: 搜尋關鍵字（如「自決」「大陸礁層」「領海」）
        treaty_name: 限定搜尋的公約（留空搜全部）
    """
    results = []
    targets = {}

    if treaty_name:
        key = _resolve_treaty(treaty_name)
        if key:
            targets[key] = _treaties[key]
        else:
            return {"success": False, "error": f"找不到「{treaty_name}」"}
    else:
        targets = _treaties

    for key, data in targets.items():
        treaty_display = data.get("treaty_zh", data["treaty"])
        for a in data["articles"]:
            # Search in title + content, both zh and en
            searchable = a.get("title_zh", "") + a.get("title_en", "") + a.get("content_zh", "") + a.get("content_en", "")
            if keyword in searchable:
                for field in ["title_zh", "content_zh", "title_en", "content_en"]:
                    if field in a and keyword in a[field]:
                        snippet = _extract_snippet(a[field], keyword)
                        break
                else:
                    snippet = _extract_snippet(searchable, keyword)
                results.append({
                    "treaty": treaty_display,
                    "treaty_key": key,
                    "article": a["article"],
                    "snippet": snippet,
                })

    return {
        "success": True,
        "keyword": keyword,
        "count": len(results),
        "results": results[:30],
    }


def _extract_snippet(text: str, keyword: str, context: int = 80) -> str:
    """Extract a snippet around the keyword."""
    idx = text.find(keyword)
    if idx < 0:
        return text[:150]
    start = max(0, idx - context)
    end = min(len(text), idx + len(keyword) + context)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


if __name__ == "__main__":
    mcp.run(transport="stdio")
