import openai
import requests
from APIKEY import API_KEY

# Set the OpenAI API key


def get_user_preferences():
    print("Welcome to the Personalized Study Assistant!")
    subject = input("What subject are you studying? ")
    hours = int(input("How many hours per day can you dedicate? "))
    days = int(input("How many days do you have to study? "))
    return {"subject": subject, "hours": hours, "days": days}

def create_study_plan(preferences):
    hours_per_day = preferences['hours']
    total_days = preferences['days']
    subject = preferences['subject']

    topics = [
        "Introduction", "Chapter 1", "Chapter 2",
        "Chapter 3", "Chapter 4", "Conclusion"
    ]

    plan = {}
    for day in range(1, total_days + 1):
        topic=topics[(day-1)%len(topics)]   # Cycle through topics
        plan[f"Day {day}"] = f"Study {hours_per_day} hours on {topic} of {subject}"
    return plan

def save_study_plan(preferences, plan):
    with open("study_plan.txt", "w") as file:
        file.write("User Preferences:\n")
        file.write(f"Subject: {preferences['subject']}\n")
        file.write(f"Hours per day: {preferences['hours']}\n")
        file.write(f"Days to study: {preferences['days']}\n\n")
        file.write("Study Plan:\n")
        for day, task in plan.items():
            file.write(f"{day}: {task}\n")


def generate_daily_task(subject,topics):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    tasks = {}

    for day,topic in enumerate(topics,start=1):
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for helping students to study."},
                {"role": "user", "content": f"Provide effective tips or resources for studying {subject}."}
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result=response.json()

            tasks[f"day {day}"] = result['choices'][0]['message']['content'].strip()
        else:
            tasks[f"day {day}"] = f"error: {response.status_code}"

    return tasks


# Main script workflow
preferences = get_user_preferences()
subject = preferences['subject']

# Generate and save the study plan
study_plan = create_study_plan(preferences)
save_study_plan(preferences, study_plan)

print("\nYour Study Plan:")
for day, task in study_plan.items():
    print(f"{day}: {task}")


# Use OpenAI API with requests to get study tips
try:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for helping students to study."},
            {"role": "user", "content": f"Provide effective tips or resources for studying {subject}."}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        tips=result['choices'][0]['message']['content'].strip() # Save tips to a file['message']['content'].strip()
        print("\nStudy Tips and Resources:")
        print(tips)

        # Save tips to a file
        with open("Study_tips.txt", "w") as file:
            file.write("Study Tips and Resourses:\n")
            file.write(tips)
    else:
        print(f"Error: {response.status_code}, {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")


topics = [
        "Introduction", "Chapter 1", "Chapter 2",
        "Chapter 3", "Chapter 4", "Conclusion"
    ]
tasks=generate_daily_task(subject,topics)

print("\ndetailed Daily study Tasks:")
for day, task in tasks.items():
    print(f"{day}: {task}")

# Save tips to a file
with open("daily_tasks.txt", "w") as file:
    file.write("detailed Daily study Tasks:\n")
    for day,task in tasks.items():
        file.write(f"{day}: {task}\n")