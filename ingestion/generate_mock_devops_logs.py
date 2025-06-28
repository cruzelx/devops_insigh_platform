import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

# Initialize Faker for realistic data
fake = Faker()

# --- Configuration ---
NUM_PULL_REQUESTS = 2500       # Number of PR lifecycles to simulate
NUM_COMMITS = 10000             # Number of individual commit events to simulate
NUM_BUILDS = 3000               # Number of CI build lifecycles to simulate
TIME_SPAN_DAYS = 90             # Generate data for the last 90 days
OUTPUT_FILE_PATH = "./data/raw/devops_events.json"

# --- Data Generation Constants ---
authors = [fake.user_name() for _ in range(30)]
repos = [f"{random.choice(['api', 'web', 'service', 'platform'])}-{fake.slug()}" for _ in range(20)]
branches = ["main", "develop", "feature/login-flow", "feature/payment-integration", "bugfix/db-connection-leak", "release/v1.2.0"]
ci_tools = ["Jenkins", "GitHub Actions", "GitLab CI/CD", "CircleCI"]
pr_titles = [
    "feat: Add new API endpoint",
    "fix: Resolve bug in user authentication",
    "docs: Update README with new instructions",
    "refactor: Improve code readability",
    "chore: Update dependencies",
    "feat: Implement new caching strategy",
    "test: Add unit tests for component X"
]
environments = ["development", "staging", "production"]

# --- Helper Functions ---

def generate_timestamp(start_time_str, end_time_str):
    """Generates a random timestamp between two given timestamps."""
    if isinstance(start_time_str, str):
        start_time = datetime.fromisoformat(start_time_str)
    else:
        start_time = start_time_str
    
    if isinstance(end_time_str, str):
        end_time = datetime.fromisoformat(end_time_str)
    else:
        end_time = end_time_str

    return start_time + timedelta(seconds=random.randint(0, int((end_time - start_time).total_seconds())))

def generate_commit_log(author, repo, branch, commit_hash, timestamp):
    """Generates a detailed commit event."""
    return {
        "event_id": str(uuid.uuid4())[:8],
        "event_type": "commit_pushed",
        "timestamp": timestamp.isoformat(),
        "repo_name": repo,
        "author_username": author,
        "commit_hash": commit_hash,
        "branch": branch,
        "message": fake.bs(),
        "lines_added": random.randint(1, 200),
        "lines_removed": random.randint(0, 100)
    }

def generate_pr_lifecycle_events(pr_id, author, repo, target_branch, source_branch, pr_title, start_time):
    """Generates a series of events for a single pull request lifecycle."""
    events = []
    
    # 1. PR Opened
    pr_opened_time = generate_timestamp(start_time, start_time + timedelta(hours=1))
    events.append({
        "event_id": str(uuid.uuid4())[:8],
        "event_type": "pull_request_opened",
        "timestamp": pr_opened_time.isoformat(),
        "pr_id": pr_id,
        "repo_name": repo,
        "author_username": author,
        "target_branch": target_branch,
        "source_branch": source_branch,
        "title": pr_title,
        "labels": random.sample(["bug", "enhancement", "docs", "backend", "frontend"], k=random.randint(0, 3)),
        "state": "open"
    })

    # 2. PR Reviewed (Optional)
    if random.random() < 0.8:
        review_time = generate_timestamp(pr_opened_time, pr_opened_time + timedelta(days=random.randint(1, 3)))
        events.append({
            "event_id": str(uuid.uuid4())[:8],
            "event_type": "pull_request_reviewed",
            "timestamp": review_time.isoformat(),
            "pr_id": pr_id,
            "reviewer_username": random.choice([u for u in authors if u != author]),
            "repo_name": repo,
            "review_status": random.choice(["APPROVED", "CHANGES_REQUESTED", "COMMENTED"]),
            "state": "open"
        })

    # 3. PR Merged or Closed
    if random.random() < 0.9:
        pr_merged_time = generate_timestamp(events[-1]['timestamp'], datetime.now())
        events.append({
            "event_id": str(uuid.uuid4())[:8],
            "event_type": "pull_request_merged",
            "timestamp": pr_merged_time.isoformat(),
            "pr_id": pr_id,
            "repo_name": repo,
            "merger_username": random.choice(authors),
            "state": "merged"
        })
    else:
        pr_closed_time = generate_timestamp(events[-1]['timestamp'], datetime.now())
        events.append({
            "event_id": str(uuid.uuid4())[:8],
            "event_type": "pull_request_closed",
            "timestamp": pr_closed_time.isoformat(),
            "pr_id": pr_id,
            "repo_name": repo,
            "state": "closed"
        })
    
    return events

def generate_ci_build_events(build_id, commit_hash, repo, branch, author, start_time):
    """Generates a series of events for a single CI build."""
    events = []
    
    # 1. Build Started
    build_start_time = generate_timestamp(start_time, start_time + timedelta(minutes=1))
    events.append({
        "event_id": str(uuid.uuid4())[:8],
        "event_type": "build_started",
        "timestamp": build_start_time.isoformat(),
        "build_id": build_id,
        "ci_tool": random.choice(ci_tools),
        "repo_name": repo,
        "commit_hash": commit_hash,
        "branch": branch,
        "triggered_by": author,
        "status": "in_progress"
    })

    # 2. Test Report (Optional)
    build_duration_seconds = random.randint(120, 1800)
    build_end_time = build_start_time + timedelta(seconds=build_duration_seconds)
    
    test_run_time = generate_timestamp(build_start_time, build_end_time)
    total_tests = random.randint(50, 500)
    
    if random.random() < 0.9:
        failed_tests = 0
        status = "success"
    else:
        failed_tests = random.randint(1, int(total_tests * 0.1))
        status = "failed"
    
    events.append({
        "event_id": str(uuid.uuid4())[:8],
        "event_type": "test_report",
        "timestamp": test_run_time.isoformat(),
        "build_id": build_id,
        "repo_name": repo,
        "test_suite": "unit_and_integration",
        "total_tests": total_tests,
        "passed_tests": total_tests - failed_tests,
        "failed_tests": failed_tests,
        "status": "completed"
    })

    # 3. Build Finished
    events.append({
        "event_id": str(uuid.uuid4())[:8],
        "event_type": "build_finished",
        "timestamp": build_end_time.isoformat(),
        "build_id": build_id,
        "repo_name": repo,
        "status": status,
        "duration_seconds": build_duration_seconds
    })

    return events

def generate_deployment_events(build_id, repo, commit_hash, build_end_time):
    """Generates a deployment lifecycle based on a successful build."""
    events = []
    
    if random.random() < 0.8:
        deployment_start_time = generate_timestamp(build_end_time, build_end_time + timedelta(minutes=10))
        deployment_id = f"DEPLOY-{random.randint(1000, 9999)}"
        environment = random.choice(environments)
        
        events.append({
            "event_id": str(uuid.uuid4())[:8],
            "event_type": "deployment_started",
            "timestamp": deployment_start_time.isoformat(),
            "deployment_id": deployment_id,
            "service_name": repo,
            "commit_hash": commit_hash,
            "build_id": build_id,
            "environment": environment,
            "status": "in_progress"
        })
        
        deployment_duration = random.randint(30, 300)
        deployment_end_time = deployment_start_time + timedelta(seconds=deployment_duration)
        
        if random.random() < 0.95:
            status = "succeeded"
        else:
            status = "failed"
            
        events.append({
            "event_id": str(uuid.uuid4())[:8],
            "event_type": "deployment_finished",
            "timestamp": deployment_end_time.isoformat(),
            "deployment_id": deployment_id,
            "service_name": repo,
            "environment": environment,
            "status": status,
            "duration_seconds": deployment_duration
        })
        
    return events


# --- Main Generation Logic (using a generator) ---
def generate_complex_devops_logs_stream():
    """
    Generates a stream of DevOps log events using a Python generator.
    This function will yield one event at a time.
    """
    base_time = datetime.now() - timedelta(days=TIME_SPAN_DAYS)
    
    print(f"Generating a stream of complex mock DevOps logs for the last {TIME_SPAN_DAYS} days...")

    # We need to collect commits to link builds/deployments later.
    # In a real streaming system, you'd process them as they arrive.
    # For this mock, we'll generate and store them in memory temporarily.
    # This is a trade-off for simplicity in the generator logic.
    all_commits = []

    # A. Generate Pull Request lifecycles
    print(f"-> Generating {NUM_PULL_REQUESTS} pull request lifecycles...")
    for _ in range(NUM_PULL_REQUESTS):
        pr_id = f"PR-{random.randint(1000, 9999)}"
        author = random.choice(authors)
        repo = random.choice(repos)
        target_branch = "main"
        source_branch = random.choice(branches)
        pr_title = random.choice(pr_titles)
        
        start_time = generate_timestamp(base_time, datetime.now() - timedelta(days=7))
        
        # Yield each event in the PR lifecycle
        for event in generate_pr_lifecycle_events(pr_id, author, repo, target_branch, source_branch, pr_title, start_time):
            yield event

    # B. Generate individual commits (not always tied to a PR)
    print(f"-> Generating {NUM_COMMITS} individual commit events...")
    for _ in range(NUM_COMMITS):
        author = random.choice(authors)
        repo = random.choice(repos)
        branch = random.choice(branches)
        commit_hash = str(uuid.uuid4())[:7]
        timestamp = generate_timestamp(base_time, datetime.now())
        
        commit_event = generate_commit_log(author, repo, branch, commit_hash, timestamp)
        yield commit_event
        
        # Store a simplified version for later linking.
        all_commits.append({
            "commit_hash": commit_hash, 
            "repo_name": repo, 
            "branch": branch, 
            "author_username": author, 
            "timestamp": timestamp
        })

    # C. Generate CI build logs, linking them to commits
    print(f"-> Generating {NUM_BUILDS} CI build lifecycles...")
    for _ in range(NUM_BUILDS):
        if not all_commits:
            print("Warning: No commits available to link builds to. Skipping build generation.")
            break
        
        build_id = f"BUILD-{random.randint(10000, 99999)}"
        
        # Pick a random commit to base the build on
        commit_info = random.choice(all_commits)
        
        # Use the commit's info to create the build
        build_events = generate_ci_build_events(
            build_id, 
            commit_info['commit_hash'], 
            commit_info['repo_name'], 
            commit_info['branch'], 
            commit_info['author_username'], 
            commit_info['timestamp']
        )
        
        # Yield each event in the build lifecycle
        for event in build_events:
            yield event

            # D. Generate deployment logs if the build was successful
            if event['event_type'] == 'build_finished' and event['status'] == 'success':
                deployment_events = generate_deployment_events(
                    build_id, 
                    commit_info['repo_name'], 
                    commit_info['commit_hash'], 
                    datetime.fromisoformat(event['timestamp'])
                )
                # Yield each event in the deployment lifecycle
                for dep_event in deployment_events:
                    yield dep_event

    print("\nStream generation complete.")


# --- Main Execution (Revised for generator) ---
if __name__ == "__main__":
    
    # Create the raw data directory if it doesn't exist
    Path(OUTPUT_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    # Create a generator object
    log_generator = generate_complex_devops_logs_stream()
    
    # We will now write the stream to a file to demonstrate the concept.
    # In a real application, you would send this to Kafka or another stream destination.
    generated_count = 0
    with open(OUTPUT_FILE_PATH, "w") as f:
        # Start the JSON array
        f.write("[\n")
        
        # Use a flag to handle the comma separation for the JSON array
        first_event = True
        
        # Iterate over the generator to get each event
        for event in log_generator:
            if not first_event:
                f.write(",\n")
            
            # Serialize the event to JSON and write to file
            json.dump(event, f, indent=2)
            
            first_event = False
            generated_count += 1
            
            # Optional: Add a small, realistic delay to simulate a real-time stream.
            # This is great for testing streaming pipelines.
            # time.sleep(random.uniform(0.01, 0.5)) 
            
        # End the JSON array
        f.write("\n]\n")

    print(f"Successfully generated {generated_count} events and saved to {OUTPUT_FILE_PATH}")