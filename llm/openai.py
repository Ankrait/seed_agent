from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    api_key="",
    base_url="http://127.0.0.1:1234/v1",
    model_name="qwen/qwen3-vl-8b"
)
