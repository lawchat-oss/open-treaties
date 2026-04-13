# open-treaties

**English** · [繁體中文](README.md)

A structured bilingual (Chinese–English) dataset of 28 international treaties — 1,914 articles with full preambles. Every article includes both Traditional Chinese and English text.

Available as JSON files for direct use in legal research, AI applications, education, or any scenario requiring structured treaty data. Also ships with an MCP server for AI assistant integration.

---

## Why open source this

International treaty texts are scattered across different sites with inconsistent formatting, and bilingual versions are even harder to find. We structured them once and open-sourced the result so others don't have to repeat the work.

---

## Included treaties

| Category | Treaty | Key | Articles |
|---|---|---|---:|
| **United Nations** | UN Charter | un-charter | 111 |
| | ICJ Statute | icj-statute | 70 |
| **Law of the Sea** | UNCLOS | unclos | 320 |
| **Human Rights** | ICCPR | iccpr | 53 |
| | ICESCR | icescr | 31 |
| | ICCPR Optional Protocol 1 | iccpr-op1 | 14 |
| | ICCPR Optional Protocol 2 | iccpr-op2 | 11 |
| | OP-ICESCR | op-icescr | 22 |
| | UDHR | udhr | 30 |
| | CAT | cat | 33 |
| | CEDAW | cedaw | 30 |
| | CRC | crc | 54 |
| | CRPD | crpd | 50 |
| | ICERD | icerd | 25 |
| **Treaty Law** | VCLT | vclt | 85 |
| **Diplomatic/Consular** | VCDR | vcdr | 53 |
| | VCCR | vccr | 79 |
| **IHL** | Geneva Convention I | gc-i | 64 |
| | Geneva Convention II | gc-ii | 63 |
| | Geneva Convention III | gc-iii | 143 |
| | Geneva Convention IV | gc-iv | 159 |
| | Additional Protocol I | gc-ap1 | 102 |
| | Additional Protocol II | gc-ap2 | 28 |
| **International Criminal Law** | Rome Statute | rome-statute | 131 |
| | Genocide Convention | genocide | 19 |
| **Anti-Corruption** | UNCAC | uncac | 71 |
| **Refugee Law** | Refugee Convention | refugee | 46 |
| **Space Law** | Outer Space Treaty | outer-space | 17 |
| | **Total** | | **1,914** |

---

## Data format

One JSON file per treaty, unified schema:

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

| Field | Description |
|---|---|
| `treaty` / `treaty_zh` | Treaty name in Chinese |
| `treaty_en` | Official English name |
| `total_articles` | Total article count |
| `preamble_zh` / `preamble_en` | Preamble (bilingual) |
| `articles[].article` | Article number (Chinese numerals) |
| `articles[].title_zh` | Article title in Chinese (8 treaties have titles; empty string if none) |
| `articles[].title_en` | Article title in English |
| `articles[].content_zh` | Article text in Chinese |
| `articles[].content_en` | Article text in English |

---

## Usage

### Browse online

**https://lawchat-oss.github.io/open-treaties/**

Individual pages for each treaty:
- Article TOC for quick navigation
- Language toggle (中文 / English / Bilingual)
- Permanent link per article (e.g. `treaties/unclos.html#art-二百八十七`)

Local preview: `cd docs && python3 -m http.server 8080`

### Direct JSON access

```python
import json

with open("data/unclos.json", encoding="utf-8") as f:
    unclos = json.load(f)

for a in unclos["articles"]:
    if a["article"] == "二百八十七":
        print(a["content_zh"])
        print(a["content_en"])
```

### MCP Server (AI assistant integration)

```bash
git clone https://github.com/lawchat-oss/open-treaties.git
cd open-treaties
python3 -m venv .venv
.venv/bin/pip install -e .
```

| Tool | Description |
|---|---|
| `list_treaties()` | List all available treaties |
| `query_treaty(treaty_name, article_no)` | Query a specific article (fuzzy name matching) |
| `search_treaty(keyword)` | Full-text search across all treaties |

---

## Project layout

```
open-treaties/
├── data/               # 28 treaties as structured bilingual JSON
├── docs/               # GitHub Pages static site
│   ├── index.html            # Landing page (categorized)
│   └── treaties/             # 28 individual treaty pages
├── server.py           # MCP server (3 tools, optional)
├── generate_site.py    # Static site generator (regenerates docs/)
├── scripts/            # Dev-only tools
│   ├── fetch_treaty.py
│   └── validate_treaties.py
├── pyproject.toml
├── LICENSE
├── DATA_LICENSE        # Data license (CC0 1.0)
├── CITATION.cff        # Academic citation metadata
└── README.md
```

---

## Data sources

Chinese translations are sourced from four tiers:

- **Taiwan official translations** (9 treaties): [Laws & Regulations Database](https://law.moj.gov.tw/) — ICCPR, ICESCR, CEDAW, CRC, CRPD, VCDR, VCCR, ICERD, UNCAC
- **Taiwan government agencies** (2 treaties): [MOJ Human Rights Portal](https://www.humanrights.moj.gov.tw/) (UDHR), [Covenants Watch](https://covenantswatch.org.tw/) (CAT)
- **Wikisource Traditional Chinese** (10 treaties): UN Charter, VCLT, UNCLOS, ICJ Statute, Rome Statute, Outer Space Treaty, OP-ICESCR, Genocide Convention, Refugee Convention, Additional Protocol II. All marked `{{PD-UN}}` on Wikisource (public domain per UN Administrative Instruction ST/AI/189/Add.9/Rev.2).
- **UN official Chinese** (7 treaties): Geneva Conventions I–IV, Additional Protocol I, ICCPR OP1/OP2. Chinese is one of the six official UN languages. The originals are in Simplified Chinese; this dataset converts them to Traditional Chinese via OpenCC without content modification.

English texts from [OHCHR](https://www.ohchr.org/), [UN Treaty Collection](https://treaties.un.org/), and [ICRC](https://www.icrc.org/).

This project provides a query tool only and does not constitute legal advice.

---

## Acknowledgements

We gratefully acknowledge the following institutions and platforms for their Chinese translations:

- [Laws & Regulations Database, Ministry of Justice, R.O.C.](https://law.moj.gov.tw/)
- [Ministry of Justice Human Rights Portal](https://www.humanrights.moj.gov.tw/)
- [Covenants Watch Taiwan](https://covenantswatch.org.tw/)
- [Wikisource](https://zh.wikisource.org/)
- [United Nations](https://www.un.org/zh/)

---

## Data update policy

This dataset is a **static release** reflecting treaty texts as of the time of collection. We do not actively track amendments or new protocols.

If you find errors or need updates, please open an [Issue](https://github.com/lawchat-oss/open-treaties/issues) or start a [Discussion](https://github.com/lawchat-oss/open-treaties/discussions). Pull requests are welcome.

---

## License

- **Code**: [MIT License](LICENSE)
- **Data**: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (Public Domain Dedication) — Free to use, modify, and distribute for any purpose. No permission or attribution required. We chose CC0 to ensure zero barriers for legal tech and academic reuse. For academic citation, see [CITATION.cff](CITATION.cff).

---

## About

Maintained by [lawchat.com.tw](https://lawchat.com.tw). Questions: [Issues](https://github.com/lawchat-oss/open-treaties/issues), [Discussions](https://github.com/lawchat-oss/open-treaties/discussions), or opensource@lawchat.com.tw.
