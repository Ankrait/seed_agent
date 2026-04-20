from langchain_deepseek import ChatDeepSeek
from config import config

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=config.DEEPSEEK_KEY,
)

# from langchain_openai import ChatOpenAI

# llm = ChatOpenAI(
#     api_key="",
#     base_url="https://89fe241d-b6f4-4e49-b3d5-9ed3c91dbe2f.tunnel4.com/v1",
# )
