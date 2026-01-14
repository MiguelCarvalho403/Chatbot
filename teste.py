import yaml

def deco(func):
    #print(nome)
    def wrapper(*args, **kwargs):
        func(*args, *kwargs)
        print("deco")
    return wrapper

@deco
def Hello():
    print(f'Hello')

Hello()
#wrap = deco("tes12")(Hello)
#print(wrapper(Hello))



def read_yaml(path: str)->dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def write_yaml(path: str, data: dict, overwrite: bool=False)->None:
    if not overwrite:
        with open(path, "r") as f:
            existing_data = yaml.safe_load(f)
        update_data = {**existing_data, **data}
        
    with open(path, "w") as f:
        yaml.dump(update_data, f, default_flow_style=False)

path_sys = "system_prompt.yaml"
path_model = "config/model_config.yaml"

#print(read_yaml(path_model))

