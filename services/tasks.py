import httpx
from pydantic import BaseModel
from config import config


class Task(BaseModel):
    title: str
    description: str


async def get_tasks_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'https://platform.brojs.ru/jrnl-bh/api/course/list',
            headers={'Authorization': f'Bearer {config.BROJS_KEY}'}
        )
        data = response.json()
        if not data.get('success'):
            return []

        courses = data.get('body')

        course_id = None
        for el in courses:
            if el.get('name') == 'KFU-26-1':
                course_id = el.get('_id')
                break

        if not course_id:
            return []

        lesson_response = await client.get(
            f'https://platform.brojs.ru/jrnl-bh/api/submission/my?courseId={course_id}',
            headers={'Authorization': f'Bearer {config.BROJS_KEY}'}
        )
        lesson_data = lesson_response.json()
        if not lesson_data.get('success'):
            return []

        tasks = lesson_data.get('body')

        result: list[Task] = []

        for task in tasks:
            if task.get('answer').get('type') != 'link':
                result.append(
                    Task(
                        title=task.get('task').get('title'),
                        description=task.get('task').get('description')
                    )
                )

        return result
