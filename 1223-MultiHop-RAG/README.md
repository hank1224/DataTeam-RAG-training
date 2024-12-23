# CivilCode-plan-execute-Bot

MultiHop + RAG + Agent 的民法問題解答Bot

## 具體執行流程

![image](https://github.com/hank1224/DataTeam-RAG-training/blob/main/static/1223-CivilCode-Arch.png)

1. 問題輸入
2. Planning Node: 將問題拆解成多個子任務
3. Agent Excuter: 逐個接收子任務並使用工具完成
4. Agent可使用工具包含：
    - `search_civilcode_by_embedding`: 使用語意相似度搜尋（向量）。
    - `search_civilcode_by_articleNumber`: 指定條文編號。
    - `show_all_civilcode_index`: 顯示民法所有編章節。
    - `search_civilcode_by_index`: 可以指定編章節，將給予該編章節的所有條文。
5. 對於各個子任務，Agent 將會確保已使用工具查詢到足夠的資訊，才會結束該子任務。
6. 所有子任務完成後，Agent 將會進行推論。
7. RePlan Node: 若推論結果不足以回答問題，Agent 將會新增子任務嘗試繼續收集資料做推論。
8. 最終回答或達到最大迭代次數停止。

## 使用資料

民法全文（110-01-20版本），條文編號：1~1125，總計共1439筆。[全國法規資料庫 - 民法](https://law.moj.gov.tw/LawClass/LawAllPara.aspx?pcode=B0000001)

資料清洗過程詳見：[資料清洗.md](./data-pre-process/README.md)

## 使用技術

- MultiHop
    - 將問題拆解成多個子任務，每個任務給予 Agent 解決，並透過子任務的答案推導出最終答案。
- RAG
    - 使用 RAG 作為知識庫，製作工具給Agent使用，使其能存取民法正本知識。
- Agent
    - 作為思考推斷引擎，考慮查找的知識是否足夠，子任務的答案集合是否足夠好，以及如何推導出最終答案。

## Evaluation

使用國考選擇題考題，選用 `113年公務人員特種考試司法人員、法務部調查局調查人員及海岸巡防人員考試` 之選擇題部分。

考題需與當時的民法版本相符，此問題已被考慮並且已選用適合的版本。

- 民法：110-01-20 修訂版本
- 試卷：113年