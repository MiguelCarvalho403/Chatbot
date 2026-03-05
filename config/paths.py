from pathlib import Path
from Testes import utils

ROOT = Path(__file__).parent.parent.resolve()
TOOLS = ROOT / Path("chatbot/tools/tools_description.yaml")
MODEL_CONFIG = ROOT / Path("config/model_config.yaml")
VECTOR_STORE = ROOT / Path("metadados/VectorStore")

if __name__ == "__main__":
    print(TOOLS)
    print(VECTOR_STORE)
    pass
