import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

authors = ["Alex","Vanessa","John","Peter","Krish","Lee"]
base_time = datetime.now()-timedelta(days=60)

modules = ["module1","module2","module3","module4","module5","module6","module7","module8","module9","module10"]

def generate_mock_events(num_events):
    events = []
    for _ in range(num_events):
        author = random.choice(authors)
        
        event_time = base_time + timedelta(seconds=random.randint(0, 60*60*24*60))
        event_type = random.choice(["push","pull_request","issue","commit"])
        
        if event_type == "push":
            module = random.choice(modules)
            message = f"{author} pushed to {module}"
        elif event_type == "pull_request":
            module = random.choice(modules)
            message = f"{author} created a pull request for {module}"
        elif event_type == "issue":
            module = random.choice(modules)
            message = f"{author} created an issue for {module}"
        elif event_type == "commit":
            module = random.choice(modules)
            message = f"{author} committed to {module}"
        
        event = {
            "id": str(uuid.uuid4())[:8],
            "author": author,
            "event_time": event_time.isoformat(),
            "event_type": event_type,
            "message": message
        }
        events.append(event)
    return events

Path("data/raw").mkdir(parents=True,exist_ok=True)
with open("./data/raw/github_events.json","w") as f:
    json.dump(generate_mock_events(10000),f,indent=2)