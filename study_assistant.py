import requests
import logging
from APIKEY import API_KEY


# Set the OpenAI API key



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
    except requests.RequestException as e:
        logging.error(f"Error fetching topics: {e}")
        topics = [f"Day {i}: Placeholder topic" for i in range(1, preferences['days'] + 1)]

    if len(topics) < preferences['days']:
        print(f"Warning: Not enough topics for {preferences['days']} days. Topics will repeat.")

    plan = {}
    for day in range(1, preferences['days'] + 1):
        topic = topics[(day - 1) % len(topics)]  # Cycle through topics if not enough
        plan[f"Day {day}"] = f"Study {preferences['hours']} hours on {topic}"

    return plan


def save_study_plan(preferences, plan):
    with open("study_plan.txt", "w") as file:
        file.write("=== User Preferences ===\n")
        file.write(f"Subject: {preferences['subject']}\n")
        file.write(f"Hours per day: {preferences['hours']}\n")
        file.write(f"Days to study: {preferences['days']}\n\n")
        file.write("=== Study Plan ===\n")
        for day, task in plan.items():
            file.write(f"{day}: {task}\n")


def generate_daily_task(subject, topics):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    tasks = {}  # Properly initialize tasks as a dictionary

    for day, topic in enumerate(topics, start=1):
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for creating study tasks."},
                {"role": "user",
                 "content": f"Provide a detailed list of study tasks for the topic '{topic}' in the subject '{subject}', focusing on practical steps and resources."}

            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if result is None:
                tasks = fallback_tasks(topics)
            tasks[f"Day {day}"] = result['choices'][0]['message']['content'].strip()
        except requests.RequestException as e:
            logging.error(f"Error fetching tasks for {topic}: {e}")
            tasks[f"Day {day}"] = f"Error: Could not generate tasks for {topic}"

    return tasks


def fallback_tasks(topics):
    return {f"Day {i+1}": f"Review the topic: {topic}" for i, topic in enumerate(topics)}






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

# Main script workflow
preferences = get_user_preferences()
subject = preferences['subject']

# Generate and save the study plan
study_plan = create_study_plan(preferences)
save_study_plan(preferences, study_plan)

print("\nYour Study Plan:")
for day, task in study_plan.items():
    print(f"{day}: {task}")

# Generate detailed daily tasks
topics = [task.split("on ")[-1] for task in study_plan.values()]  # Extract topics from the plan
tasks = generate_daily_task(subject, topics)

print("\nDetailed Daily Study Tasks:")
for day, task in tasks.items():
    print(f"{day}: {task}")

# Track and save progress
# track_progress(tasks)


