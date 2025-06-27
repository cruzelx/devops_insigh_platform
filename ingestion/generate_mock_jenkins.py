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
        event_time = base_time+timedelta(seconds=random.randint(0,60*60*24*60))
        duration = random.randint(1,20)
        
        event_type = random.choice(["build","deploy","test","release"])
        
        if event_type == "build":
            message = f"{author} built the project"
        elif event_type == "deploy":
            message = f"{author} deployed the project"
        elif event_type == "test":
            message = f"{author} tested the project"
        elif event_type == "release":
            message = f"{author} released the project"
            
        status = random.choice(["success","failure"])
        
        event = {
            "id": i,
            "author": author,
            "event_time": event_time.isoformat(),
            "event_type": event_type,
            "message": message,
            "duration": duration,
            "status": status
        }
        events.append(event)
    return events

print("Generating mock jenkins events...")
Path("data/raw").mkdir(parents=True,exist_ok=True)
with open("./data/raw/jenkins_events.json","w") as f:
    json.dump(generate_mock_events(1000),f,indent=2)

print("Mock jenkins events generated successfully")