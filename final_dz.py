# Каждое дело должно характеризоваться четырьмя полями:
# 1 title— название задачи;
# 2 priority— текстовое описание приоритета (low, normal, high);
# 3 isDone— выполнено ли задание;
# 4 id— уникальное число— идентификатор задачи.

# 1. Создание задачи. Отправляется POST-запрос на сервер по пути /tasks с
#    телом в виде JSON с полями title и priority. Сервер должен создать и
#    сохранить задачу, выставить isDone в False, выдать задаче уникальный ID и
#    в ответ отправить JSON со всеми четырьмя полями.
# 2. Получение списка всех задач. Отправляется GET-запрос на сервер по
#    пути /tasks, в ответ приходит список задач в формате JSON. Пример: [{"title":
#    "Gym", "id": 1, "priority": "low", "isDone": false}, {"title": "Buy a laptop", "id": 2,
#    "priority": "high", "isDone": true}].
# 3. Отметка о выполнении задачи. Отправляется POST-запрос на сервер по
#    пути /tasks/id/complete, где id— это уникальный идентификатор задачи. В
#    ответ приходит пустое тело ответа с кодом 200, если всё успешно, и кодом
#    404, если такой задачи нет.

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse


STORAGE_FILE_NAME = "tasks.txt"

current_tasks = []

if os.path.exists(STORAGE_FILE_NAME):
    with open(STORAGE_FILE_NAME, "r") as file:
        current_tasks = json.load(file)
else:
    with open(STORAGE_FILE_NAME, "w") as file:
        json.dump([], file)


def save_tasks():
    with open(STORAGE_FILE_NAME, "w") as file:
        json.dump(current_tasks, file)


class ToDoHandler(BaseHTTPRequestHandler):
    def __response_data(self, status_code = 200, head = None):
        self.send_response(status_code)
        if head:
            self.send_header(head['key'], head['value'])
        self.end_headers()

    def do_GET(self):
        def render_form():
            return """
                <form action="/tasks" method="post" style="margin-bottom: 42px;">
                    <label>
                      название задачи:
                      <input type="text" name="title">
                    </label>
                    <select id="priority" name="priority">
                      <option value="low">low</option>
                      <option value="normal">normal</option>
                      <option value="high">high</option>
                    </select>
                    <button type="submit">Сохранить</button>
                </form>
            """
        def render_html(item):
            return f"""
                <li style="{'color: rgba(0, 200, 0, 1);' if item["isDone"] else 'color: tomato;'} font-size: 24px; display: flex;">
                    {item["title"]}
                    <span>&nbsp-&nbsp{item["priority"]}</span>
                    <button onclick="fetch('/tasks/{item["id"]}/{'uncomplete' if item["isDone"] else 'complete'}', {{'method': 'POST'}}).then(() => location.reload())" style="margin: 0 0 0 auto; cursor: pointer;"> {'Отменить выполнение' if item["isDone"] else 'Выполнить'}</button>
                </li>
            """

        if self.path == "/tasks":
            self.__response_data(200, {'key': 'Content-type', 'value': 'text/html;charset=utf-8'})
            self.wfile.write("""
                        <html>
                            <head>
                            <title>dz-final</title>
                            </head>
                            <body>
                                <main style="display: flex; align-items:center; justify-content: center; height: 100vh; width: 100%;">
                                    <sections>
                                        {form}
                                        <ul style="display: flex; flex-direction: column; gap: 12px; list-style: none; padding: 0;">
                                          {tasks}
                                        </ul>
                                    </section>
                                </main>
                            </body>
                        </html>
                    """.format(
                            form=render_form(),
                            tasks="\n".join(map(render_html, current_tasks))
                        ).encode('utf-8'))
        else:
            self.__response_data(404)

    def do_POST(self):
        if self.path == "/tasks":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            try:
                data = urllib.parse.parse_qs(body.decode('utf-8'))
                print(data)
                title = data.get("title", [None])[0]
                priority = data.get("priority", [None])[0]

                if title is None or priority is None:
                    raise ValueError("Invalid data")

                new_task = {
                    "id": len(current_tasks) + 1,
                    "title": title,
                    "priority": priority,
                    "isDone": False,
                }
                current_tasks.append(new_task)
                save_tasks()

                self.__response_data(302, {'key': 'Location', 'value': '/tasks'})
            except (ValueError, json.JSONDecodeError):
                self.__response_data(400)

        elif self.path.startswith("/tasks/"):
            is_status =  True if self.path.endswith("/complete") else False
            try:
                task_id = int(self.path.split("/")[2])
                task = next((task for task in current_tasks if task["id"] == task_id), None)
                if not task:
                    self.__response_data(404)
                    return

                task["isDone"] = is_status
                save_tasks()
                self.__response_data(200)
            except ValueError:
                self.__response_data(400)
        else:
            self.__response_data(404)


def run(server_class=HTTPServer, handler_class=ToDoHandler, port=8008):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    run()