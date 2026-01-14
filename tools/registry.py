from icecream import ic
import yaml

def write_yaml(path: str, data: dict, overwrite: bool=False)->None:
    if not overwrite:
        with open(path, "r") as f:
            existing_data = yaml.safe_load(f)
        if existing_data is not None:
            update_data = {**existing_data, **data}
        else:
            update_data = data
                
    with open(path, "w") as f:
        yaml.dump(update_data, f, default_flow_style=False)

def registry_function(func):
      
    doc = func.__doc__
    name = func.__name__
    data = {name: doc}
    path = "/home/migueldcarvalho/Projetos/Chatbot/config/tools_doc.yaml"

    write_yaml(path=path, data=data)

    return func

if __name__ == "__main__":
    pass