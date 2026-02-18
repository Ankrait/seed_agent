from langchain_core.tools import tool

from llm.openai import llm


@tool
def get_weather(city: str, date: str) -> str:
    """Get the weather for a city on a specific date."""
    result = llm.invoke(
        f'Какая погода в {city} {date}'
    )
    return result.content
