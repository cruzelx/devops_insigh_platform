import json
import random
from datetime import datetime, timedelta
from pathlib import Path

authors = ["Alex","Vanessa","John","Peter","Krish","Lee"]
base_time = datetime.now()-timedelta(days=60)

def generate_mock_events(num_events):
    events = []
    for i in range(num_events):
        author = random.choice(authors)
        deployment_time = base_time+timedelta(seconds=random.randint(0,60*60*24*60))
        environment = random.choice(["staging","production"])
        status = random.choice(["success","failure"])
        
        event = {
            "id": i,
            "author": author,
            "deployment_time": deployment_time.isoformat(),
            "environment": environment,
            "status": status
        }
        events.append(event)
    return events

print("Generating mock deployments...")
Path("data/raw").mkdir(parents=True,exist_ok=True)
with open("./data/raw/deployments.json","w") as f:
    json.dump(generate_mock_events(10000),f,indent=2)

print("Mock deployments generated successfully")