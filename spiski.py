import json

class Task:
    def __init__(self, name):
        self.name = name
        self.done = False

    def show_info(self):
            print(f" Задача {self.name}, Статус:{self.done}")

    def mark_done(self):
            self.done=True

try:
    with open("tasks.json", "r", encoding="utf-8") as file:
        loaded_data = json.load(file)
        tasks=[]
        for item in loaded_data:
            t=Task(item["name"])
            t.done= item["done"]
            tasks.append(t)
except (FileNotFoundError, json.JSONDecodeError):    
    tasks=[]

def show_tasks(tasks):
    if len(tasks) == 0:
        print("список задачь пуст. ")
    else:
        print("Ваши задачи. ")
        for index, task in enumerate(tasks,start=1):
            if task.done==True:
                print(f"{index}. [x] {task.name}")
            else:

                print(f"{index}. [ ]  {task.name}")

def add_tasks(tasks):
    task_name=input("Что нужно cделать? ").strip()
    if task_name=="":
        print("Строка не может быть пустой! ")
        return
    new_task=Task(task_name)
    tasks.append(new_task)
    print("Задача добавлена. ")    

def delete_tasks(tasks):
    try:
        task_num=int(input("Введите номер задачи. "))
        tasks.pop(task_num-1)
        print("Задача удалена! ")
    except (ValueError, IndexError):
        print("не правельно")

def mark_done(tasks):
    try:
        task_num=int(input("Введите номер выполнения? "))
        tasks[task_num - 1].mark_done()
        print("Задача отмечена как выполнена! ")
    except (ValueError, IndexError):
        print("Не правильно")

while True:
    print("1. Показать задачи. ")
    print("2. добавить задачу. ")
    print("3. Удолить задачу.")
    print("4. Отметить как выполненную. ")
    print("5. Выйти")
    try:
        choice=int(input("Введите действие"))
    except ValueError:
        print("Ошибка! Введите цыфру! ")
        continue
    if choice == 1:
       show_tasks(tasks)
    elif choice == 2:
       add_tasks(tasks) 
    elif choice == 3:
        delete_tasks(tasks)
    elif choice == 4:
        mark_done(tasks)
    elif choice == 5:
        tasks_to_save=[task.__dict__ for task in tasks]
        with open("tasks.json", "w", encoding="utf=8") as file:
            json.dump(tasks_to_save, file, ensure_ascii=False, indent=4)
        print("Задачи сохранены. До встречи.")
        break
    else:
        print(" Такой команды нет. ")

