from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

from llm.openai import llm


# @tool
# def get_weather(city: str, date: str) -> str:
#     """Get the weather for a city on a specific date."""
#     result = llm.invoke(
#         [
#             SystemMessage(
#                 'Ты агент подсказывающий погоду по городу и дате. Если у тебя нет данных, то придумай погоду'
#             ),
#             HumanMessage(
#                 f'Какая погода в {city} {date}?'
#             )
#         ]

#     )
#     return result.content


tools = []
