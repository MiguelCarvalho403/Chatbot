from graph import chat_graph

from langgraph.types import Command

import uuid
import gc

graph = chat_graph()

config = {'configurable': {
    'thread_id': uuid.uuid4()
}}
user_text = input("Digite Algo> ")
graph.invoke({'messages': [user_text]}, config)

#ic(graph.get_state(config)) # Retorna os estado atual do grafo
while True:
    
    user_text = input("Digite Algo> ")

    if user_text == 'quit':
        break
    
    command = Command(resume=user_text)

    graph.invoke(command, config)

del graph
gc.collect