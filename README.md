# open-treaties

[English](README.en.md) · **繁體中文**

國際法公約中英雙語條文查詢 — 28 部公約、1,914 條條文，JSON + MCP server，法律研究、AI 應用、教學直接用。

每條條文提供繁體中文與英文對照，附完整序言。

---

## 為什麼開源這個

國際法公約散落各處，格式不統一，中英對照更難找。結構化一次、開源出來，讓做法律研究和法律 AI 的人不用再重複這個苦工。

---

## 收錄公約

| 分類 | 公約 | 代碼 | 條文數 |
|---|---|---|---:|
| **聯合國** | 聯合國憲章 | un-charter | 111 |
| | 國際法院規約 | icj-statute | 70 |
| **海洋法** | 聯合國海洋法公約 | unclos | 320 |
| **人權** | 公民與政治權利國際公約 | iccpr | 53 |
| | 經濟社會文化權利國際公約 | icescr | 31 |
| | ICCPR 第一任擇議定書 | iccpr-op1 | 14 |
| | ICCPR 第二任擇議定書（廢除死刑） | iccpr-op2 | 11 |
| | OP-ICESCR 任擇議定書 | op-icescr | 22 |
| | 世界人權宣言 | udhr | 30 |
| | 禁止酷刑公約 | cat | 33 |
| | 消除對婦女一切形式歧視公約 | cedaw | 30 |
| | 兒童權利公約 | crc | 54 |
| | 身心障礙者權利公約 | crpd | 50 |
| | 消除一切形式種族歧視國際公約 | icerd | 25 |
| **條約法** | 維也納條約法公約 | vclt | 85 |
| **外交/領事** | 維也納外交關係公約 | vcdr | 53 |
| | 維也納領事關係公約 | vccr | 79 |
| **國際人道法** | 日內瓦第一公約（傷病） | gc-i | 64 |
| | 日內瓦第二公約（海上傷病） | gc-ii | 63 |
| | 日內瓦第三公約（戰俘） | gc-iii | 143 |
| | 日內瓦第四公約（平民） | gc-iv | 159 |
| | 第一附加議定書 | gc-ap1 | 102 |
| | 第二附加議定書 | gc-ap2 | 28 |
| **國際刑法** | 羅馬規約 | rome-statute | 131 |
| | 防止及懲治滅絕種族罪公約 | genocide | 19 |
| **反貪腐** | 聯合國反腐敗公約 | uncac | 71 |
| **難民法** | 關於難民地位的公約 | refugee | 46 |
| **太空法** | 外太空條約 | outer-space | 17 |
| | **合計** | | **1,914** |

---

## 資料格式

每部公約一個 JSON 檔，統一 schema：

```json
{
  "treaty": "維也納條約法公約",
  "treaty_zh": "維也納條約法公約",
  "treaty_en": "Vienna Convention on the Law of Treaties",
  "total_articles": 85,
  "preamble_zh": "本公約當事各國...",
  "preamble_en": "The States Parties to the present Convention...",
  "articles": [
    {
      "article": "一",
      "title_zh": "本公約之範圍",
      "title_en": "Scope of the present Convention",
      "content_zh": "本公約適用於國家間之條約。",
      "content_en": "The present Convention applies to treaties between States."
    }
  ]
}
```

| 欄位 | 說明 |
|---|---|
| `treaty` / `treaty_zh` | 公約中文名稱 |
| `treaty_en` | 公約英文正式名稱 |
| `total_articles` | 條文總數 |
| `preamble_zh` | 中文序言 |
| `preamble_en` | 英文序言 |
| `articles[].article` | 條號（中文數字） |
| `articles[].title_zh` | 條文標題中文（部分公約有，無標題則為空字串） |
| `articles[].title_en` | 條文標題英文 |
| `articles[].content_zh` | 條文中文內容 |
| `articles[].content_en` | 條文英文內容 |

> 條號以中文數字儲存（如「二百八十七」）。8 部公約（VCLT、UNCLOS、Rome Statute、CRPD、UNCAC、Refugee、GC-AP1、GC-AP2）有條文標題，其餘公約原文無獨立標題。完整 schema 定義見 [`schema/treaty.json`](schema/treaty.json)。

---

## 使用方式

### 線上瀏覽

**https://lawchat-oss.github.io/open-treaties/**

28 部公約各自獨立頁面，支援：
- 條號目錄（TOC）快速跳轉
- 中文 / English / 雙語切換
- 每條條文有永久連結（如 `treaties/unclos.html#art-二百八十七`）

本地預覽：`cd docs && python3 -m http.server 8080`

### 直接使用 JSON 資料

```python
import json

with open("data/unclos.json", encoding="utf-8") as f:
    unclos = json.load(f)

# 查第 287 條
for a in unclos["articles"]:
    if a["article"] == "二百八十七":
        print(a["content_zh"])
        print(a["content_en"])
```

### MCP Server（AI 助手查詢）

本 repo 附帶一個 MCP server，提供 3 個工具讓 AI 助手查詢條文。

```bash
# 安裝
git clone https://github.com/lawchat-oss/open-treaties.git
cd open-treaties
python3 -m venv .venv
.venv/bin/pip install -e .

# 驗證
.venv/bin/python -c "
import asyncio
from server import mcp
tools = asyncio.run(mcp.list_tools())
print([t.name for t in tools])
"
```

#### MCP 工具

| 工具 | 說明 |
|---|---|
| `list_treaties()` | 列出所有可查詢的公約 |
| `query_treaty(treaty_name, article_no)` | 查特定公約的特定條文（支援模糊名稱匹配、中文數字條號） |
| `search_treaty(keyword)` | 跨公約全文搜尋關鍵字 |

#### 註冊到 Claude Code

```bash
claude mcp add open-treaties -- \
  /full/path/to/open-treaties/.venv/bin/python \
  /full/path/to/open-treaties/server.py
```

---

## 專案結構

```
open-treaties/
├── data/               # 28 部公約的結構化 JSON（中英雙語）
├── docs/               # GitHub Pages 靜態網站
│   ├── index.html            # 首頁（分類瀏覽）
│   └── treaties/             # 28 個公約頁面
├── server.py           # MCP server（3 個工具，optional）
├── generate_site.py    # 靜態網站產生器（修改資料後重新生成 docs/）
├── scripts/            # 開發用工具（非運行時必要）
│   ├── fetch_treaty.py       # 公約抓取 + 解析腳本
│   └── validate_treaties.py  # JSON 品質驗證腳本
├── pyproject.toml
├── LICENSE
├── DATA_LICENSE        # 資料授權（CC0 1.0）
├── CITATION.cff        # 學術引用格式
└── README.md
```

---

## 資料來源

### 台灣官方翻譯（9 部）

| 代碼 | 公約 | 來源 |
|---|---|---|
| iccpr | 公民與政治權利國際公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| icescr | 經濟社會文化權利國際公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| cedaw | 消除對婦女一切形式歧視公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| crc | 兒童權利公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| crpd | 身心障礙者權利公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| vcdr | 維也納外交關係公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| vccr | 維也納領事關係公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| icerd | 消除一切形式種族歧視國際公約 | [全國法規資料庫](https://law.moj.gov.tw/) |
| uncac | 聯合國反腐敗公約 | [全國法規資料庫](https://law.moj.gov.tw/) |

### 台灣政府機關（2 部）

| 代碼 | 公約 | 來源 |
|---|---|---|
| udhr | 世界人權宣言 | [法務部人權大步走](https://www.humanrights.moj.gov.tw/) |
| cat | 禁止酷刑公約 | [人權公約施行監督聯盟](https://covenantswatch.org.tw/)（內政部委託） |

### 維基文庫繁體版（10 部）

| 代碼 | 公約 | 來源 |
|---|---|---|
| un-charter | 聯合國憲章 | [維基文庫](https://zh.wikisource.org/) |
| vclt | 維也納條約法公約 | [維基文庫](https://zh.wikisource.org/) |
| unclos | 聯合國海洋法公約 | [維基文庫](https://zh.wikisource.org/) |
| icj-statute | 國際法院規約 | [維基文庫](https://zh.wikisource.org/) |
| rome-statute | 國際刑事法院羅馬規約 | [維基文庫](https://zh.wikisource.org/) |
| outer-space | 外太空條約 | [維基文庫](https://zh.wikisource.org/) |
| op-icescr | ICESCR 任擇議定書 | [維基文庫](https://zh.wikisource.org/) |
| genocide | 防止及懲治滅絕種族罪公約 | [維基文庫](https://zh.wikisource.org/) |
| refugee | 關於難民地位的公約 | [維基文庫](https://zh.wikisource.org/) |
| gc-ap2 | 日內瓦第二附加議定書 | [維基文庫](https://zh.wikisource.org/) |

> 上述條約在維基文庫均標記為 `{{PD-UN}}`（Public Domain），依據聯合國行政指令 ST/AI/189/Add.9/Rev.2，條約正式文本屬公有領域。

### 聯合國官方中文版（7 部）

以下公約台灣無官方譯本。譯文來自[聯合國官方中文版](https://www.un.org/zh/)（中文為聯合國六種正式語文之一），原文以簡體字書寫，本資料集經 OpenCC 轉為繁體字呈現，內容未經修改。

| 代碼 | 公約 | 來源 |
|---|---|---|
| gc-i | 日內瓦第一公約 | 聯合國官方中文版 → 繁體字呈現 |
| gc-ii | 日內瓦第二公約 | 聯合國官方中文版 → 繁體字呈現 |
| gc-iii | 日內瓦第三公約 | 聯合國官方中文版 → 繁體字呈現 |
| gc-iv | 日內瓦第四公約 | 聯合國官方中文版 → 繁體字呈現 |
| gc-ap1 | 日內瓦第一附加議定書 | 聯合國官方中文版 → 繁體字呈現 |
| iccpr-op1 | ICCPR 第一任擇議定書 | 聯合國官方中文版 → 繁體字呈現 |
| iccpr-op2 | ICCPR 第二任擇議定書 | 聯合國官方中文版 → 繁體字呈現 |

本專案**僅提供條文查詢工具**，不構成法律意見。

---

## 致謝

本資料集之中文譯本來自以下機構與平台，特此致謝：

- [中華民國法務部全國法規資料庫](https://law.moj.gov.tw/) — 9 部公約台灣官方翻譯
- [法務部人權大步走](https://www.humanrights.moj.gov.tw/) — 世界人權宣言
- [人權公約施行監督聯盟](https://covenantswatch.org.tw/) — 禁止酷刑公約
- [維基文庫](https://zh.wikisource.org/) — 聯合國憲章、維也納條約法公約等 10 部
- [聯合國](https://www.un.org/zh/) — 日內瓦公約、ICCPR 任擇議定書等 7 部官方中文版

英文條文來自 [OHCHR](https://www.ohchr.org/)、[UN Treaty Collection](https://treaties.un.org/)、[ICRC](https://www.icrc.org/) 官方英文版。

---

## 資料更新政策

本資料集為**靜態釋出**，反映各公約截至收錄時的條文版本。本專案不主動追蹤公約修正案或新增議定書。

如有條文勘誤或新版本需要更新，歡迎透過 [Issues](https://github.com/lawchat-oss/open-treaties/issues) 或 [Discussions](https://github.com/lawchat-oss/open-treaties/discussions) 提出，也歡迎直接開 PR 貢獻。

---

## 授權

- **程式碼**：[MIT License](LICENSE)
- **資料**：[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)（公有領域貢獻）— 任何人皆可自由使用、修改及散布，無需取得授權或署名。我們選擇 CC0 是為了讓法律科技與學術研究的再利用零門檻。學術引用格式請參考 [CITATION.cff](CITATION.cff)。

---

## 關於

由 [lawchat.com.tw](https://lawchat.com.tw) 維護。問題與建議請至 [Issues](https://github.com/lawchat-oss/open-treaties/issues)、[Discussions](https://github.com/lawchat-oss/open-treaties/discussions) 或來信 opensource@lawchat.com.tw。
