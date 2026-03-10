from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent.graph import build_graph

step = 1


def print_chunk_message(chunk):
    message, meta = chunk
    global step

    if meta['langgraph_step'] != step:
        step = meta['langgraph_step']
        print('\n\nАгент:', end='', flush=False)
        if meta['langgraph_node'] == 'tool_call':
            print('*Вызов функции*', end='', flush=False)

    if message.content and meta['langgraph_node'] == 'call_model':
        print(message.content, end='', flush=False)


def main():
    memory = InMemorySaver()
    agent = build_graph().compile(
        checkpointer=memory, interrupt_before=['tool_call']
    )

    def run(state: dict | None, config: dict):
        for chunk in agent.stream(
            state, config,
            stream_mode=['updates', 'messages']
        ):
            chunk_type, chunk_data = chunk
            current_state = agent.get_state(config)

            if chunk_type == 'updates':
                if chunk_data.get('call_model'):
                    pass
                if chunk_data.get('__interrupt__') == () and current_state.next == ('tool_call',):
                    tool_call = (
                        current_state.values
                        .get('messages')[-1].tool_calls[0]
                    )

                    print('\n\n=========================')
                    print(
                        f'Вызов {tool_call.get('name')}: {tool_call.get('args')}'
                    )
                    answer = input('Подтвердите запуск? (y/n) ')
                    if answer.lower() == 'y':
                        run(None, config)
                    else:
                        break
            elif chunk_type == 'messages':
                print_chunk_message(chunk_data)

    while True:
        user = input('\nВы: ')
        if user.lower() == 'exit' or user.lower() == 'выход':
            break

        run(
            {
                "messages": [
                    SystemMessage(f'Ты агент по погоде. Сегодня 19.02.2026'),
                    HumanMessage(user)
                ]
            },
            {'configurable': {'thread_id': 'temp'}}
        )


if __name__ == "__main__":
    main()
