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
        "Authorization": f"Bearer {preferences['apiKey']}"
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
        topics = [
            topic.lstrip("-").strip() if ":" in topic or "-" in topic else topic.strip()
            for topic in topics
            if topic.strip()
        ]


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


def generate_daily_task(subject, topics,api_key):
    """
    Generates tasks dynamically for all topics related to the given subject.
    Uses batch processing to ensure faster and complete generation without placeholders.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Batch prompt to generate tasks for all topics
    prompt = (
        f"Generate detailed study tasks for the following topics related to {subject}:\n"
        "- Each task should include:\n"
        "  - A title matching the topic.\n"
        "  - A detailed task description.\n"
        "  - Estimated time to complete.\n"
        "  - The study key points.\n"
        "  - Recommended resources (book, video, and website with links).\n\n"
        + "\n".join([f"- {topic}" for topic in topics])
    )

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are helping to create a detailed study plan."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # Make a single API request to generate tasks for all topics
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        # Parse the response into tasks
        task_list = response.json()["choices"][0]["message"]["content"].strip().split("\n\n")
        tasks = {}
        for i, task_content in enumerate(task_list):
            if i < len(topics):  # Ensure tasks align with topics
                tasks[f"Task {i + 1}"] = f"Topic: {topics[i]}\n{task_content.strip()}"
        return tasks

    except requests.RequestException as e:
        logging.error(f"Error fetching tasks: {e}")
        return {f"Task {i + 1}": fallback_task(topics[i]) for i in range(len(topics))}


def fallback_task(topic):
    """
    Generate a fallback task if the API fails to return a valid task.
    """
    return (
        f"Topic: {topic}\n"
        f"Task Description: Learn and research about '{topic}' in detail.\n"
        f"Estimated Time: 2-3 hours\n"
        f"The key points: Machine Learning"
        f"Recommended Resources:\n"
        f"- Book: 'Artificial Intelligence: A Modern Approach'\n"
        f"- Website: Coursera course 'AI For Everyone'\n"
        f"- Video: 'Introduction to AI' by AI Academy"
    )



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
    """
    Get the information from app.py(preferences), which includes subject, hours, days, key points.
    Use this info to create study plan and task, package it up then return, showing it on the screen
    """
    study_plan = create_study_plan(preferences)
    topics = [task.split("on ", 1)[-1].strip() for task in study_plan.values()]

    tasks = generate_daily_task(preferences["subject"], topics,preferences['apiKey'])

    return {
        "study_plan": study_plan,
        "tasks": tasks,
    }