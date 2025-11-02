import json, os
def save_checkpoint(file, project, count):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file,"w") as f: json.dump({project:count},f)

def load_checkpoint(file, project):
    if not os.path.exists(file): return 0
    try:
        with open(file) as f:
            return json.load(f).get(project,0)
    except: return 0