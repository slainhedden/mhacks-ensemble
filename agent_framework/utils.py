import os

def get_agent_filepath(name: str) -> str:
    agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
    os.makedirs(agents_dir, exist_ok=True)
    return os.path.join(agents_dir, f"{name}.json")