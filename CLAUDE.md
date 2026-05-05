# CLAUDE.md

Этот файл содержит инструкции для Claude Code при работе с данным репозиторием.

## Общее описание проекта

Это агент на LangGraph, который:
1. Получает задачи из API BroJS (список заданий для курса)
2. Для каждой задачи создаёт план выполнения (исследуя проект)
3. Выполняет план — делает изменения в файлах
4. Делает git commit и push
5. Возвращает ссылку на коммит

Проект `project/` — это отдельный git-репозиторий (_remote: git@github.com:Ankrait/seed_agent.git_), в котором нужно выполнять задания.

## Текущая архитектура (реализовано)

### Граф агента (`agent/graph.py`)

```
START → TASKS_LIST → TAKE_TASK → CREATE_PLAN → READ_PROJECT_TOOL ↔ CREATE_PLAN → END
```

- `TASKS_LIST` — получает задачи из BroJS API
- `TAKE_TASK` — берёт первую задачу из списка
- `CREATE_PLAN` — LLM изучает проект и создаёт план выполнения
- `READ_PROJECT_TOOL` — выполняет инструменты чтения проекта (find_file_by_name, find_code_by_regex, read_file_lines)
- После READ_PROJECT_TOOL возвращается в CREATE_PLAN для продолжения планирования

### Файлы и их назначение

```
agent/
  graph.py      # Определение графа, маршрутизация should_tool_call, has_tasks_to_do
  state.py      # State (messages, tasks, current_task, plan), Stage enum
  node.py       # Реализация узлов: tasks_list_node, take_task_node, create_plan_node
  tools.py      # Инструменты чтения проекта: find_file_by_name, find_code_by_regex, read_file_lines
  prompts.py    # Системный промпт для создания плана (CREATE_PLAN_SYSTEM_PROMPT)

llm/
  deepseek.py   # LLM (DeepSeek Chat)
  openai.py     # LLM (OpenAI, для project/ поддиректории)

services/
  tasks.py      # Task модель, get_tasks_list() — запрос к BroJS API

config.py       # Pydantic BaseSettings: DEEPSEEK_KEY, BROJS_KEY
main.py         # Точка входа, запуск с InMemorySaver + interrupt_before
```

### Состояние графа (`agent/state.py`)

```python
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # история сообщений
    tasks: list[Task]           # оставшиеся задачи
    current_task: Task | None   # текущая задача
    plan: str | None            # план выполнения (пока текст)

class Stage(StrEnum):
    TASKS_LIST = 'tasks_list'
    TAKE_TASK = 'take_task'
    CREATE_PLAN = 'create_plan'
    READ_PROJECT_TOOL = 'read_project_tool'
```

### Инструменты чтения (`agent/tools.py`)

```python
read_project_tools = [find_code_by_regex, find_file_by_name, read_file_lines]
```

- `find_file_by_name(regexp)` — ищет файлы по regex в project/
- `find_code_by_regex(pattern)` — ищет код по regex в project/
- `read_file_lines(filename, start_line, end_line)` — читает строки файла

### Промпт планирования (`agent/prompts.py`)

LLM получает задачу и должен:
- Минимальным количеством вызовов понять структуру проекта
- Составить план: какой файл, какие строки, что делать (добавить/изменить/удалить)
- Вывести план текстом

## Что нужно добавить (план реализации)

### 1. Инструменты записи (`agent/tools.py`)

Нужны инструменты для выполнения плана:

```python
@tool
def write_file(filepath: str, content: str) -> str:
    """Создать/перезаписать файл в project/"""

@tool
def edit_file(filepath: str, start_line: int, end_line: int, new_content: str) -> str:
    """Изменить строки файла в project/"""

@tool
def delete_file(filepath: str) -> str:
    """Удалить файл в project/"""

execute_tools = [write_file, edit_file, delete_file]
```

### 2. Git операции (`agent/git_tools.py`) — новый файл

```python
PROJECT_DIR = Path(__file__).parent.parent / 'project'

def git_add(files: list[str] | None = None) -> tuple[bool, str]:
    """Stage файлы для коммита"""

def git_commit(message: str) -> tuple[bool, str]:
    """Создать коммит"""

def git_push() -> tuple[bool, str]:
    """Push в remote"""

def get_commit_url() -> str:
    """Получить URL коммита (https://github.com/user/repo/commit/hash)"""
```

Все операции выполняются в директории `project/` через `subprocess.run(..., cwd=PROJECT_DIR)`.

### 3. Новые узлы (`agent/node.py`)

```python
def execute_plan_node(state: State) -> State:
    """Выполняет план: итерируется по steps и вызывает write/edit/delete"""
    # plan = {'steps': [{action, filepath, start_line, end_line, content}, ...], 'commit_message': '...'}
    # Для каждого step вызывает соответствующий tool
    return {'execution_results': [...]}

def git_operations_node(state: State) -> State:
    """git add → git commit → git push → get_commit_url"""
    return {'commit_url': 'https://...'}

def return_result_node(state: State) -> State:
    """Добавляет финальное сообщение с ссылкой на коммит"""
    return {'messages': [HumanMessage(f"Готово. Коммит: {commit_url}")]}
```

### 4. Новые стадии (`agent/state.py`)

```python
class Stage(StrEnum):
    # ... существующие ...
    EXECUTE_PLAN = 'execute_plan'       # выполнение плана
    GIT_OPERATIONS = 'git_operations'   # git add/commit/push
    RETURN_RESULT = 'return_result'    # возврат результата
```

Новые поля в State:
```python
plan: ExecutionPlan | None  # {'steps': [...], 'commit_message': '...'}
execution_results: list[str] | None
commit_url: str | None
```

Типы:
```python
class PlanStep(TypedDict):
    action: Literal["edit", "write", "delete"]
    filepath: str
    start_line: Optional[int]
    end_line: Optional[int]
    content: Optional[str]

class ExecutionPlan(TypedDict):
    steps: list[PlanStep]
    commit_message: str
```

### 5. Обновлённый граф (`agent/graph.py`)

```
START → TASKS_LIST → TAKE_TASK → CREATE_PLAN → READ_PROJECT_TOOL ↔ CREATE_PLAN
                                                               ↓
                                                         EXECUTE_PLAN
                                                               ↓
                                                     GIT_OPERATIONS
                                                               ↓
                                                     RETURN_RESULT → END
```

```python
def should_execute_or_read(state: State):
    """После CREATE_PLAN: если есть tool_calls — читаем, иначе выполняем"""
    if state['messages'][-1].tool_calls:
        return Stage.READ_PROJECT_TOOL
    return Stage.EXECUTE_PLAN
```

### 6. Новый промпт (`agent/prompts.py`)

Изменить CREATE_PLAN_SYSTEM_PROMPT, чтобы LLM выводил JSON:
```python
CREATE_PLAN_SYSTEM_PROMPT = """
ВЫВОДИ ТОЛЬКО JSON (без markdown блоков):
{
    "steps": [
        {"action": "write|edit|delete", "filepath": "...", "start_line": null|int, "end_line": null|int, "content": "...|null"}
    ],
    "commit_message": "сообщение коммита на русском"
}
"""
```

### 7. Обновлённый main.py

Добавить `Stage.GIT_OPERATIONS` в `interrupt_before`:
```python
agent = build_graph().compile(
    checkpointer=memory,
    interrupt_before=[Stage.READ_PROJECT_TOOL, Stage.GIT_OPERATIONS]
)
```

## Формат JSON плана

```json
{
    "steps": [
        {"action": "write", "filepath": "main.py", "start_line": null, "end_line": null, "content": "full content here"},
        {"action": "edit", "filepath": "agent/tools.py", "start_line": 10, "end_line": 20, "content": "new content"},
        {"action": "delete", "filepath": "old_file.py", "start_line": 1, "end_line": 5, "content": null}
    ],
    "commit_message": "добавлена функция X в agent/tools.py"
}
```

## Команды для запуска

```bash
# Активировать виртуальное окружение
source .venv/bin/activate

# Запустить агента в интерактивном режиме
python main.py

# Тестировать async
python main.py  # вызывает test()

# Проверить компиляцию графа
python -c "from agent.graph import build_graph; build_graph().compile()"
```

## Важные детали

1. **Git в project/** — все git операции работают в поддиректории `project/`, так как это отдельный репозиторий
2. **interrupt_before** — `Stage.READ_PROJECT_TOOL` прерывает перед чтением файлов, `Stage.GIT_OPERATIONS` перед git операциями
3. **InMemorySaver** — сохраняет состояние между вызовами, нужен `thread_id` в конфиге
4. **DEEPSEEK_KEY, BROJS_KEY** — берутся из `.env` файла
