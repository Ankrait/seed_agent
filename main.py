from langchain_core.messages import SystemMessage, HumanMessage

from agent.graph import build_graph


def main():

    graph = build_graph()
    result = graph.compile().stream(
        {
            "messages": [
                HumanMessage(f'Хочу миллион рублей')
            ],
        },
        stream_mode="updates"
    )

    for chunk in result:
        first_chunk = chunk.get('get_first_wish')
        add_wish_chunk = chunk.get('add_wish')

        if first_chunk:
            print(
                f'Желание пользователя: {first_chunk.get('wish_history')[-1]}'
            )
        elif add_wish_chunk:
            if add_wish_chunk.get("current_status") == 'wish':
                status = 'плохое'
            else:
                status = 'хорошее'

            print(
                f'Добавлено {status} желание: {add_wish_chunk.get('wish_history')[-1]}'
            )


if __name__ == "__main__":
    main()
