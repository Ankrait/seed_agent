import asyncio

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agent.graph import build_graph
from agent.state import Stage

step = 1


def print_chunk_message(chunk):
    message, meta = chunk
    global step

    if meta['langgraph_step'] != step:
        step = meta['langgraph_step']
        print('\n\nАгент:', end='', flush=False)
        if meta['langgraph_node'] == Stage.READ_PROJECT_TOOL:
            print('*Вызов функции*', end='', flush=False)

    if message.content and meta['langgraph_node'] == Stage.CREATE_PLAN:
        print(message.content, end='', flush=False)


def main():
    memory = InMemorySaver()
    agent = build_graph().compile(
        checkpointer=memory, interrupt_before=[Stage.READ_PROJECT_TOOL]
    )

    def run(state: dict | None, config: dict):
        for chunk in agent.stream(
            state, config,
            stream_mode=['updates', 'messages']
        ):
            chunk_type, chunk_data = chunk
            current_state = agent.get_state(config)

            if chunk_type == 'updates':
                if chunk_data.get(Stage.CREATE_PLAN):
                    pass
                if chunk_data.get('__interrupt__') == () and current_state.next == (Stage.READ_PROJECT_TOOL,):
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


async def test():
    agent = build_graph().compile()
    res = await agent.ainvoke({})
    print(res.get('message')[-1])


if __name__ == "__main__":
    # main()
    asyncio.run(test())
