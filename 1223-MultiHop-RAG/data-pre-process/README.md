# 資料前處理說明 + 如何重現

TODO: [civilcode-index-110-01-20.json](./civilcode-index-110-01-20.json) 這部分目前是用chatGPT生的，**仍有錯誤**。

## TL;DR
1. [民法-110-01-20.html](./民法-110-01-20.html) 是原始資料
2. `民法-110-01-20.html` 拿給 [extract_metadata.py](./extract-metadata.py) 處理，得到 `民法-110-01-20.json`
3. `民法-110-01-20.json` 拿給 [convert-to-openai-batchAPI-jsonl.py](./convert-to-openai-batchAPI-jsonl.py) 處理，得到 `civilcode-110-01-20.jsonl`
4. `civilcode-110-01-20.jsonl` 上傳到 [Batch API 處理](https://platform.openai.com/docs/api-reference/batch)，處理過後得到 `batch_*************_output.jsonl`
5. 結合 `民法-110-01-20.json` 和 `batch_*************_output.jsonl`，寫入 vector_store，這部分程式碼在 [1223-CivilCode-plan-excute.ipynb](../CivilCode-ChatBot-Notebook/1223-CivilCode-plan-excute.ipynb) 可以找到
6. 將 `民法-110-01-20.json` 存入關聯資料庫，也可以在 [1223-CivilCode-plan-excute.ipynb](../CivilCode-ChatBot-Notebook/1223-CivilCode-plan-excute.ipynb) 找到。
7. [civilcode-index-110-01-20.json](./civilcode-index-110-01-20.json) 這部分目前是用chatGPT生的，**仍有錯誤**。


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