"""
Deep Agent на основе create_deep_agent из deepagents.
Использует DeepSeek модель и встроенные файловые инструменты.
MCP интеграция с Gitea для чтения journal BroJS.
"""
import asyncio
import os
import subprocess
from pathlib import Path

from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver

from deepagents import create_deep_agent
from deepagents.backends.local_shell import LocalShellBackend
from langchain_mcp_adapters.sessions import StdioConnection
from langchain_mcp_adapters.tools import load_mcp_tools

from config import config
from services.tasks import Task, get_tasks_list


# Директория проекта
PROJECT_DIR = Path(__file__).parent / 'project'

# UVX path
UVX_PATH = '/home/linuxbrew/.linuxbrew/bin/uvx'


def get_gitea_mcp_connection() -> StdioConnection:
    """Создать MCP connection для Gitea."""
    return StdioConnection(
        transport='stdio',
        command=UVX_PATH,
        args=[
            '--refresh',
            '--extra-index-url',
            'https://nikitatsym.github.io/gitea-mcp/simple',
            'gitea-mcp'
        ],
        cwd=str(Path(__file__).parent),
        env={
            **os.environ,
            'GITEA_URL': 'https://git.bro-js.ru',
            'GITEA_TOKEN': config.GITEA_KEY
        }
    )


async def load_gitea_tools():
    """Загрузить инструменты из Gitea MCP."""
    connection = get_gitea_mcp_connection()
    tools = await load_mcp_tools(session=None, connection=connection)
    return tools


def get_commit_url() -> str | None:
    """Получить URL коммита."""
    try:
        # Получаем последний коммит
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%s'],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            if len(parts) >= 1:
                commit_hash = parts[0]
                # Получаем remote URL
                remote_result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    cwd=PROJECT_DIR,
                    capture_output=True,
                    text=True
                )
                if remote_result.returncode == 0:
                    remote = remote_result.stdout.strip()
                    # Конвертируем git@github.com:user/repo.git в https://github.com/user/repo
                    if remote.startswith('git@github.com:'):
                        repo_path = remote.replace('git@github.com:', '').replace('.git', '')
                        return f"https://github.com/{repo_path}/commit/{commit_hash}"
                    elif remote.startswith('https://'):
                        return f"{remote.replace('.git', '')}/commit/{commit_hash}"
        return None
    except Exception as e:
        print(f"Error getting commit URL: {e}")
        return None


def create_agent(mcp_tools: list | None = None):
    """Создать deep agent с DeepSeek моделью и MCP инструментами."""
    # Используем ChatDeepSeek напрямую
    model = ChatDeepSeek(
        model='deepseek-chat',
        api_key=config.DEEPSEEK_KEY,
    )

    # Создаём backend с правильной директорией и shell доступом
    backend = LocalShellBackend(root_dir=str(PROJECT_DIR), virtual_mode=False)

    # Все инструменты
    tools = mcp_tools if mcp_tools else []

    agent = create_deep_agent(
        model=model,
        backend=backend,
        tools=tools,
        system_prompt="""Ты агент по решению задач курса BroJS.

У тебя есть доступ к Gitea MCP серверу через инструменты:
- gitea_read - читать данные с Gitea (репозитории, issues, pull requests)
- gitea_version - версия сервера

Для чтения задач из BroJS journal используй gitea_read с операциями:
- list_user_repos - список репозиториев пользователя
- get_repo - получить информацию о репозитории

Работай в директории project/ — это отдельный git репозиторий.
После выполнения задачи создай коммит с осмысленным сообщением на русском языке.

Для каждой задачи:
1. Изучи структуру проекта в директории project/
2. Выполни задачу - сделай необходимые изменения
3. Создай коммит с сообщением на русском
4. Сообщи ссылку на коммит

Инструменты для работы с файлами:
- ls - посмотреть файлы
- read_file - прочитать файл
- write_file - создать/перезаписать файл
- edit_file - изменить файл
- glob, grep - поиск

После выполнения изменений используй shell (execute) для git:
1. git add -A
2. git commit -m "сообщение"
3. git push

Верни ссылку на коммит в формате: https://github.com/user/repo/commit/hash""",
    )

    return agent


async def get_tasks():
    """Получить список задач из BroJS API."""
    return await get_tasks_list()


async def run_agent_for_task(agent, task: Task, thread_config: dict):
    """Запустить агента для выполнения одной задачи."""
    user_message = f"""Задача:
Название: {task.title}
Описание: {task.description}

Выполни эту задачу в проекте project/. Сделай необходимые изменения,
создай коммит и верни ссылку на коммит."""

    result = await agent.ainvoke(
        {
            'messages': [
                SystemMessage("Ты агент по решению задач курса. Работай в директории project/."),
                HumanMessage(user_message)
            ]
        },
        thread_config
    )

    # Получаем последний ответ агента
    last_message = result['messages'][-1] if result.get('messages') else None
    return last_message.content if last_message else None


async def run_agent():
    """Запустить агента для обработки задач."""
    # Загружаем MCP инструменты из Gitea
    print("Загрузка MCP инструментов из Gitea...")
    try:
        mcp_tools = await load_gitea_tools()
        print(f"Загружено {len(mcp_tools)} MCP инструментов")
    except Exception as e:
        print(f"Не удалось загрузить MCP инструменты: {e}")
        mcp_tools = []

    agent = create_agent(mcp_tools=mcp_tools)

    memory = InMemorySaver()

    thread_config = {'configurable': {'thread_id': 'deep-agent-v1'}}

    # Пробуем получить задачи из BroJS API
    try:
        tasks = await get_tasks()
    except Exception as e:
        print(f"Не удалось получить задачи из BroJS API: {e}")
        print("Используем тестовую задачу")
        tasks = [
            Task(
                title="Тестовая задача",
                description="Создайте файл test.txt с текстом 'Hello, BroJS!'"
            )
        ]

    if not tasks:
        # Если API не вернул задачи, используем тестовую задачу
        print("Нет задач из API, используем тестовую задачу")
        tasks = [
            Task(
                title="Тестовая задача",
                description="Создайте файл test.txt с текстом 'Hello, BroJS!'"
            )
        ]

    results = []

    for i, task in enumerate(tasks):
        print(f"\n{'='*60}")
        print(f"Задача {i+1}/{len(tasks)}: {task.title}")
        print(f"{'='*60}")

        try:
            result = await run_agent_for_task(agent, task, thread_config)
            print(f"\nРезультат:\n{result}")
            results.append({
                'task': task.title,
                'result': result,
                'success': True
            })
        except Exception as e:
            print(f"\nОшибка при выполнении задачи: {e}")
            results.append({
                'task': task.title,
                'result': str(e),
                'success': False
            })

    print("\n" + "="*60)
    print("ИТОГИ:")
    print("="*60)
    for r in results:
        status = "✓" if r['success'] else "✗"
        print(f"{status} {r['task']}")
        if r['result']:
            print(f"  {r['result'][:200]}...")


async def test():
    """Тестирование агента."""
    agent = create_agent()

    result = await agent.ainvoke(
        {
            'messages': [
                HumanMessage("Привет! Скажи 'Hello' и расскажи что ты умеешь.")
            ]
        },
        {'configurable': {'thread_id': 'test'}}
    )

    print("Результат теста:")
    print(result['messages'][-1].content)


if __name__ == "__main__":
    # asyncio.run(test())
    asyncio.run(run_agent())