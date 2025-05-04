import argparse
import signal
import os
import random
import sys
from importlib import import_module
from time import sleep
import logging


TASK_CLUSTER_COUNT = 5 # Размер кластера задач 
TASK_INTERVAL_SECONDS = 10 # Время между запускаим отдельных задач 
GROUPING_INTERVAL_SECONDS = 500 # Интервал между кластерами задач 
EXTRA_DEFAULTS = [] # Дополнительные параметры задач 


def emulation_loop(workflows, clustersize, taskinterval, taskgroupinterval, extra): # Основной цикл эмуляуии
    while True:
        for c in range(clustersize): # Перебираем кластер 
            sleep(random.randrange(taskinterval))
            index = random.randrange(len(workflows)) # Выбираем случайную задачу 
            print(workflows[index].display) # Выводим её описание 
            workflows[index].action(extra) # Выполняем задачу 
        sleep(random.randrange(taskgroupinterval))


def import_workflows(): # Импорт задач 
    extensions = [] # Список, в который будем добавлять загруженные модули
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'app', 'workflows')): # При помощи os.walk проходимся по всем файлам и директориям внутри app/workflows, создаём путь к app/workflows
        files = [f for f in files if not f[0] == '.' and not f[0] == "_"] # Отбрасываем скрытые файлы
        dirs[:] = [d for d in dirs if not d[0] == '.' and not d[0] == "_"] # Отбрасываем скрытые директории
        for file in files: # Проходим по каждому найденному файлу 
            print(file) 
            try:
                extensions.append(load_module('app/workflows', file)) # Загружаем его как модуль
            except Exception as e:
                print('Error could not load workflow. {}'.format(e))
    return extensions


def load_module(root, file): # Загрузка workflow как модуля
    module = os.path.join(*root.split('/'), file.split('.')[0]).replace(os.path.sep, '.') # Преобразуем app/workflows/some_workflow.py в app.workflows.some_workflow
    workflow_module = import_module(module) # Загружаем модуль
    return getattr(workflow_module, 'load')() # Вызываем load() внутри загруженного модуля и возвращаем результат. Ожидается, что каждый workflow имеет load(), которая возвращает объект с display, action() и cleanup()


def run(clustersize, taskinterval, taskgroupinterval, extra): # Запуск процесса 
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,  # или DEBUG, если хочешь больше подробностей
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Лог в консоль
            # logging.FileHandler("human.log"),  # (опционально) лог в файл
        ]
    )
    
    random.seed()
    workflows = import_workflows() # Импорт workflows 

    def signal_handler(sig, frame): # Обработчик сигналов, который cleanup() для всех workflow перед выходом
        for workflow in workflows:
            workflow.cleanup()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler) # Обработка Ctrl+C 
    signal.signal(signal.SIGTERM, signal_handler) # Обработка завершения процесса 

    emulation_loop(workflows=workflows, clustersize=clustersize, taskinterval=taskinterval, # Запуск основного цикла
                    taskgroupinterval=taskgroupinterval, extra=extra)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Emulate human behavior on a system') # Обработка аргументов командной строки 
    parser.add_argument('--clustersize', type=int, default=TASK_CLUSTER_COUNT)
    parser.add_argument('--taskinterval', type=int, default=TASK_INTERVAL_SECONDS)
    parser.add_argument('--taskgroupinterval', type=int, default=GROUPING_INTERVAL_SECONDS)
    parser.add_argument('--extra', nargs='*', default=EXTRA_DEFAULTS)
    args = parser.parse_args()

    try:
        run(
            clustersize=args.clustersize,
            taskinterval=args.taskinterval,
            taskgroupinterval=args.taskgroupinterval,
            extra=args.extra
        )
    except KeyboardInterrupt:
        print(" Terminating human execution...")
        sys.exit()
