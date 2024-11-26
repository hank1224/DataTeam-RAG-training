"""
    This code is from: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/wait-user-input/#interacting-with-the-agent
"""

# 設定State
from langgraph.graph import MessagesState, START

# 設定工具
# 我們將有一個實際的工具 - 搜索工具
# 我們還會有一個「假」工具 - 「ask_human」工具
# 這裡我們定義任何實際的工具
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def search(query: str):
    """呼叫以瀏覽網頁，這邊寫假的"""
    return f"我查詢了：{query}。結果：舊金山天氣晴朗。"

tools = [search]
tool_node = ToolNode(tools)

# 設定模型
import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv(".env")
Azure_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]

os.environ["LANGCHAIN_TRACING_V2"] = "true"
LANGCHAIN_API_KEY = os.environ["LANGCHAIN_API_KEY"]

model = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

from pydantic import BaseModel

# 我們將「綁定」所有工具到模型
# 我們有來自上面的實際工具，但我們也需要一個模擬工具來詢問人類
# 由於 `bind_tools` 接受工具也接受工具定義，
# 我們可以為 `ask_human` 定義一個工具定義
class AskHuman(BaseModel):
    """向人類提問"""

    question: str

model = model.bind_tools(tools + [AskHuman])

# 定義節點和條件Edge

# 定義決定是否繼續的函數
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # 如果沒有 tool_calls，則結束
    if not last_message.tool_calls:
        return "end"
    # 如果工具調用是詢問人類，我們返回該節點
    # 你也可以在這裡添加邏輯讓某些系統知道需要人類輸入
    # 例如，發送通知之類的
    elif last_message.tool_calls[0]["name"] == "AskHuman":
        return "ask_human"
    # 否則，如果有工具調用，我們繼續
    else:
        return "continue"

# 定義調用模型的函數
def call_model(state):
    messages = state["messages"]
    response = model.invoke(messages)
    # 我們返回一個列表，因為這將被添加到現有列表中
    return {"messages": [response]}

# 我們定義一個假節點來詢問人類
def ask_human(state):
    pass

# 建立圖表

from langgraph.graph import END, StateGraph

# 定義一個新圖表
workflow = StateGraph(MessagesState)

# 定義我們將在其中循環的三個節點
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)
workflow.add_node("ask_human", ask_human)

# 設置入口點為 `agent`
# 這意味著這個節點是首先被調用的
workflow.add_edge(START, "agent")

# 我們現在添加一個條件Edge
workflow.add_conditional_edges(
    # 首先，我們定義起始節點。我們使用 `agent`。
    # 這意味著這些是 `agent` 節點調用後的Edge。
    "agent",
    # 接下來，我們傳入決定下一個節點的函數。
    should_continue,
    # 最後，我們傳入一個映射。
    # The keys are strings, and the values are other nodes.
    # END 是一個特殊節點，表示圖表應該結束。
    # 發生的情況是我們將調用 `should_continue`，然後其輸出將與此映射中的鍵匹配。
    # 根據匹配的結果，將調用相應的節點。
    {
        # 如果是 `tools`，那麼調用tool。
        "continue": "action",

        # 我們可能會詢問人類
        "ask_human": "ask_human",

        # 否則我們結束。
        "end": END,
    },)

# 我們現在從 `tools` 添加一個普通Edge到 `agent`。
# 這意味著調用 `tools` 之後，下一個調用 `agent` 節點。
workflow.add_edge("action", "agent")

# 在我們得到人類的回應後，我們回到代理節點
workflow.add_edge("ask_human", "agent")

# 設定記憶體
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# 最後，我們編譯它！
# 這將其編譯為一個LangChain可運行的，
# 意味著你可以像使用其他可運行的一樣使用它
# 我們在 `ask_human` 節點之前添加一個中斷點，因此它永遠不會執行
app = workflow.compile(checkpointer=memory, interrupt_before=["ask_human"])






# 現在我們可以運行它！
from langchain_core.messages import HumanMessage

config = {"configurable": {"thread_id": "2"}}
input_message = HumanMessage(
    content="使用搜索工具詢問用戶他們在哪裡，然後查詢那裡的天氣"
)
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

tool_call_id = app.get_state(config).values["messages"][-1].tool_calls[0]["id"]

# 我們現在使用ID和我們想要的回應創建工具調用
tool_message = [
    {"tool_call_id": tool_call_id, "type": "tool", "content": "san francisco"}
]

# 我們現在更新State
# 注意我們還指定了 `as_node="ask_human"`
# 這將作為這個節點應用此更新，
# 這樣之後它將繼續正常運行
app.update_state(config, {"messages": tool_message}, as_node="ask_human")

# 我們可以檢查State
# 我們可以看到State當前有下一個 `agent` 節點
# 這是基於我們如何定義我們的圖表，
# 在 `ask_human` 節點之後（我們剛剛觸發的）
# 有一條邊指向 `agent` 節點
app.get_state(config).next

# 我們現在可以告訴代理繼續。我們可以直接作為圖表的輸入傳遞None，因為不需要額外的輸入
for event in app.stream(None, config, stream_mode="values"):
    event["messages"][-1].pretty_print()