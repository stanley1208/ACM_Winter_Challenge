import requests
import logging
from APIKEY import API_KEY
import json
import os


# Remove old daily task files
def clean_up_old_files(subject):
    for file in os.listdir("."):
        if file.endswith("_daily_tasks.json") and not file.startswith(subject):
            os.remove(file)
            print(f"Deleted old file:{file}")
        if file.endswith("_study_plan.json") and not file.startswith(subject):
            os.remove(file)
            print(f"Deleted old file:{file}")



def create_study_plan(preferences):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Dynamically generate topics using GPT-4
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for creating personalized study plans."},
            {"role": "user", "content": f"Suggest study topics for {preferences['subject']} over {preferences['days']} days."}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        topics = response.json()['choices'][0]['message']['content'].strip().split("\n")
        topics=[topic.strip() for topic in topics if topic.strip()]
    except requests.RequestException as e:
        logging.error(f"Error fetching topics: {e}")
        topics = [f"Day {i}: Placeholder topic" for i in range(1, preferences['days'] + 1)]

    # Use placeholder topics if GPT response is empty
    if not topics:
        topics=[f"Topic {i}" for i in range(1, preferences['days'] + 1)]

    # Limit topics to the number of days
    topics = topics[:preferences['days']]

    cleaned_topics = [
        topic.split(":")[-1].strip() if topic.split(":")[-1].strip() else f"Topic {i + 1}"
        for i, topic in enumerate(topics)
    ]

    if not cleaned_topics[0]:
        cleaned_topics[0] = "Introduction or Overview"

    plan = {}

    for day in range(1, preferences['days'] + 1):
        topic = cleaned_topics[(day - 1) % len(cleaned_topics)]  # Cycle through topics if not enough
        plan[f"Day {day}"] = f"Study {preferences['hours']} hours on {topic}"

    return plan


def generate_daily_task(subject, topics):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    prompt = (
            f"You are a helpful assistant in helping students in Santa Clara University. For each topic below in {subject}, provide:\n"
            f"- A detailed task description.\n"
            f"- Estimated time to complete.\n"
            f"- Recommended resources (books, videos, or websites).\n\n"
            + "\n".join([f"- {topic}" for topic in topics])
    )

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for creating study tasks."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        task_list = response.json()['choices'][0]['message']['content'].strip().split("\\n")
        return {f"Task {i + 1}": task.strip() if task.strip() else "No detailed task available" for i, task in
                enumerate(task_list)}
    except requests.RequestException as e:
        logging.error(f"Error fetching tasks: {e}")
        return {f"Task {i + 1}": f"No detailed task available for {topic}" for i, topic in enumerate(topics)}


def fallback_tasks(topics):
    return {f"Day {i+1}": f"Review the topic: {topic}" for i, topic in enumerate(topics)}

def save_to_file(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    print(f"Data saved to {filename}")


def mark_completed(tasks):
    completed=set()
    try:
        with open("progress.json", "r") as file:
            completed=set(json.load(file).get("completed", []))

    except FileNotFoundError:
        pass


    choice = input("\nEnter the task you've completed (e.g., 'Task 1') or press Enter to skip: ").strip()
    if choice in tasks:
        completed.add(choice)
        print(f"Marked {choice} as completed")
        with open(f"progress.json", "w") as file:
            json.dump({"completed": list(completed)}, file)
        print("Progress saved")


def show_next_task(tasks):
    try:
        with open("progress.json", "r") as file:
            completed=set(json.load(file).get("completed", []))

    except FileNotFoundError:
        completed=set()

    for task,description in tasks.items():
        if task not in completed:
            print(f"\nReminder: {task}:{description}")
            break

def main_workflow(preferences):



    study_plan = create_study_plan(preferences)
    topics=[task.split("on ")[-1] for task in study_plan.values()]
    tasks = generate_daily_task(preferences["subject"], topics)

    return{
        "study_plan": study_plan,
        "tasks": tasks,
    }













