from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent.graph import build_graph


def main():
    memory = InMemorySaver()
    agent = build_graph().compile(checkpointer=memory)

    while True:
        user = input('\nВы: ')
        if user.lower() == 'exit' or user.lower() == 'выход':
            break

        config = {'configurable': {'thread_id': 'temp'}}
        answer = agent.invoke(
            {
                "messages": [
                    SystemMessage(f'Ты агент по погоде. Сегодня 19.02.2026'),
                    HumanMessage(user)
                ]
            },
            config
        )

        print(answer)


if __name__ == "__main__":
    main()
