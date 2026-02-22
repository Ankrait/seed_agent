from langchain_core.messages import SystemMessage, HumanMessage

from agent.graph import build_graph


def main():
    graph = build_graph()
    result = graph.compile().stream(
        {
            "messages": [
                SystemMessage(f'Ты агент по погоде. Сегодня 19.02.2026'),
                HumanMessage(f'Какая погода сегодня в Казани?')
            ],
        },
        stream_mode="updates"
    )

    for chunk in result:
        if chunk.get('call_model'):
            print(chunk.get('call_model').get('messages')[0].content)


if __name__ == "__main__":
    main()
