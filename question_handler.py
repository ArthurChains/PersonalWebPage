import json
from datetime import datetime


def question_handler(msg: str, user):
    try:
        tmp = open("questions.json", "r")
        tmp.close()
    except FileNotFoundError:
        with open("questions.json", 'w') as questions:
            json.dump({}, questions)
    with open("questions.json", "r+") as questions:
        data = json.load(questions)
        time = datetime.now().strftime('%m/%d/%Y, %H:%M:%S')

        list_of_messages = data.get(user.vk_id, [])
        list_of_messages.append({'name': user.name, 'date': time, 'message': msg})

        data.update({user.vk_id: list_of_messages})
        questions.seek(0)
        json.dump(data, questions, ensure_ascii=False, indent=2)
