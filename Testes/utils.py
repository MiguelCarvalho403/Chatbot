import yaml

def read_yaml(path: str)->dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

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