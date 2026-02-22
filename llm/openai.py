from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="",
    base_url="http://127.0.0.1:1234/v1",
    # base_url="http://172.21.13.70:1234/v1",
)
