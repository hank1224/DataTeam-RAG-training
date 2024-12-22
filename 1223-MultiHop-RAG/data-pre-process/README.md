# 資料前處理說明

## 資料來源

全國法規資料庫：[民法所有條文](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001)

抓取HTML原始碼，然後Beautify，存成 `民法-110-01-20.html`

## 資料前處理

將html檔案使用 [extract_metadata.py](./extract-metadata.py) 處理，建立條文索引，合併部分漢字編號，並存成 `民法-110-01-20.json`

## OpenAI Batch API

因為直接用 langchain 的存入 vector_store 方法沒有批次處理這個功能，會卡到 Azure API 呼叫上限。

我也懶的去查怎麼用 langchain 批次處理這東西，所以我直接用 OpenAI 的 [Batch API 處理](https://platform.openai.com/docs/api-reference/batch)。

Batch API 有限定輸入格式，所以要用 [convert-to-penai-batchAPI-jsonl.py](./convert-to-openai-batchAPI-jsonl.py) 來轉換成 `civilcode-110-01-20.jsonl`，之後上傳。

阿上傳完拿回來還要再轉一次然後再存回去 vector_store。