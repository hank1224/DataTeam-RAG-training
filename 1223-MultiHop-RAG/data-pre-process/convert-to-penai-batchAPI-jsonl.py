"""
{"custom_id": article_number, "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": [article_content],encoding_format="float"}}
{
  "custom_id": article_number,
  "method": "POST",
  "url": "/v1/embeddings",
  "body": {
    "model": "text-embedding-3-small",
    "input": [
        article_content 
    ],
    encoding_format="float"
  }
}
"""
import json

with open('1223-MultiHop-RAG/data-pre-process/民法-110-01-20.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('1223-MultiHop-RAG/data-pre-process/civilcode-110-01-20.jsonl',   'w', encoding='utf-8') as f:
    for item in data:
        jsonl_item = {
            "custom_id": item["article_number"],
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "model": "text-embedding-3-small",
                "input": item["article_content"],
                "encoding_format": "float"
            }
        }
        f.write(json.dumps(jsonl_item, ensure_ascii=False) + '\n')