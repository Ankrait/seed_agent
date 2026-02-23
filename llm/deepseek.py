from langchain_deepseek import ChatDeepSeek
from config import config

llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=config.DEEPSEEK_KEY,
)
