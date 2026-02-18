from langchain_core.messages import SystemMessage, HumanMessage

from agent.graph import build_graph


def main():
    print("Hello from seed-agent!")


if __name__ == "__main__":
    graph = build_graph()
    result = graph.compile().invoke({
        "messages": [
            SystemMessage(f'Ты агент по погоде. Сегодня 19.02.2026'),
            HumanMessage(f'Какая погода сегодня в Казани?')
        ]
    })

    print(result)
