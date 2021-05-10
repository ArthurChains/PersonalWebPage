import json
from datetime import datetime


def question_handler(msg: str, user):
    with open("questions.json", "r+", encoding='utf-8') as questions:
        data = json.load(questions)
        time = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')
        data.update({user.vk_id: {'name': user.name, 'date': time, 'message': msg}})
        questions.seek(0)
        json.dump(data, questions, ensure_ascii=False)
