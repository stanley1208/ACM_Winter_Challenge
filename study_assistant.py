import requests
import logging
from APIKEY import API_KEY
import json

def get_user_preferences():
    print("Welcome to the Personalized Study Assistant!")
    subject = input("What subject are you studying? ").strip()

    while True:
        try:
            hours = int(input("How many hours per day can you dedicate? "))
            if hours <= 0:
                raise ValueError("Hours must be greater than 0.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid number.")

    while True:
        try:
            days = int(input("How many days do you have to study? "))
            if days <= 0:
                raise ValueError("Days must be greater than 0.")
            break
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid number.")

    return {"subject": subject, "hours": hours, "days": days}


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
            f"You are a helpful assistant. For each topic below in {subject}, provide:\n"
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





# def track_progress(tasks):
#     completed = set()
#     while len(completed) < len(tasks):
#         print("\nYour Study Tasks:")
#         for day, task in tasks.items():
#             status = "✅ Completed" if day in completed else "❌ Pending"
#             print(f"{day}: {task} [{status}]")
#
#         choice = input("\nEnter the day you've completed (e.g., 'Day 1'), or type 'exit' to quit: ").strip()
#         if choice.lower() == "exit":
#             break
#         elif choice in tasks and choice not in completed:
#             completed.add(choice)
#             print(f"Marked {choice} as completed!")
#         else:
#             print("Invalid choice or already marked as completed.")
#
#     # Save progress to a file
#     with open("study_progress.txt", "w") as file:
#         for day, task in tasks.items():
#             status = "✅ Completed" if day in completed else "❌ Pending"
#             file.write(f"{day}: {task} [{status}]\n")
#

def main_workflow():
    preferences = get_user_preferences()
    study_plan = create_study_plan(preferences)

    print("\nYour Study Plan:\n"+"="*30)
    for day, task in study_plan.items():
        print(f"{day}:\n {task}\n")

    topics = [task.split("on ")[-1] for task in study_plan.values()]
    tasks = generate_daily_task(preferences['subject'], topics)
    save_to_file("daily_tasks.json", tasks)

    save_to_file(f"{preferences['subject']}_study_plan.json", {"preferences": preferences, "study_plan": study_plan})
    save_to_file(f"{preferences['subject']}_daily_tasks.json", tasks)

    print("\nDetailed Daily Study Tasks:\n"+"="*30)
    for task, description in tasks.items():
        print(f"{task}: {description}\n")

    def show_reminder(tasks):
        print("\nToday's Task Reminder:")
        first_task = next(iter(tasks.items()))
        print(f"{first_task[0]}: {first_task[1]}")

    show_reminder(tasks)



# Track and save progress
# track_progress(tasks)


main_workflow()
