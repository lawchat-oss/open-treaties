# 貢獻指南

感謝你對 Open Treaties 的興趣！以下說明如何參與貢獻。

## 歡迎的貢獻

- **新增公約**：提交新的國際公約資料（需附官方來源連結）
- **翻譯修正**：修正現有條文的中文或英文翻譯錯誤
- **條文標題補充**：為尚無標題的公約補充條文標題
- **Schema 改進**：改善 JSON 結構或新增有用欄位
- **靜態網站改進**：改善 `docs/` 的瀏覽體驗
- **MCP server 改進**：增強查詢功能

## 不接受的貢獻

- **自行翻譯的版本**：本資料集僅收錄官方翻譯或公認權威來源的譯本
- **非官方來源的條文**：所有條文必須能追溯到官方或可驗證的公開來源
- **AI 生成的翻譯**：不接受機器翻譯作為條文內容

## 提交 PR 前

1. **確認來源**：新增或修改的條文必須附上官方來源連結
2. **跑驗證腳本**：
   ```bash
   python scripts/validate_treaties.py
   ```
   確保所有 JSON 通過驗證（無重複條號、無空條文、條文數一致）
3. **遵循 schema**：JSON 結構請參考 `schema/treaty.json`
4. **重新生成靜態站**（如果改了 `data/`）：
   ```bash
   python generate_site.py
   ```

## 資料格式

每部公約一個 JSON 檔，放在 `data/` 目錄下。完整 schema 定義見 [`schema/treaty.json`](schema/treaty.json)。

## 授權

提交 PR 即表示你同意你的貢獻以本專案的授權條款發布：程式碼 MIT、資料 CC0 1.0。

## 問題與討論

- 開 [Issue](https://github.com/lawchat-oss/open-treaties/issues) 回報問題
- 到 [Discussions](https://github.com/lawchat-oss/open-treaties/discussions) 提問或討論
- 來信 opensource@lawchat.com.tw
