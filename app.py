from flask import Flask, request, render_template
from study_assistant import main_workflow  # Import your study assistant function
from flask import send_file
import io


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")  # HTML form for user input


@app.route("/download_txt", methods=["POST"])
def download_txt():
    """
    Download function
    """
    from ast import literal_eval  # Use safer eval alternative

    # Retrieve content from the form
    study_plan = request.form.get("study_plan", "{}")
    tasks = request.form.get("tasks", "{}")

    # Convert strings to dictionaries
    try:
        study_plan_dict = literal_eval(study_plan)
        tasks_dict = literal_eval(tasks)
    except (ValueError, SyntaxError):
        study_plan_dict = {}
        tasks_dict = {}

    # Format study plan and tasks
    formatted_study_plan = "\n".join([f"{day}: {task}" for day, task in study_plan_dict.items()])
    formatted_tasks = "\n\n".join([f"{task}:\n{details}" for task, details in tasks_dict.items()])

    # Combine content
    file_content = f"Your Study Plan:\n\n{formatted_study_plan}\n\nDetailed Daily Study Tasks:\n\n{formatted_tasks}"

    # Create in-memory text file
    output = io.BytesIO()
    output.write(file_content.encode("utf-8"))
    output.seek(0)

    # Serve the file as a download
    return send_file(output, as_attachment=True, download_name="study_plan.txt", mimetype="text/plain")

@app.route("/generate", methods=["GET", "POST"])
def generate():
    """
    Get the information from the user, package it up then transfer to main_workflow to handle
    """
    subject = request.form.get("subject", "").strip()
    hours = int(request.form.get("hours", 0))
    days = int(request.form.get("days", 0))
<<<<<<< HEAD
    keyPoints = request.form.getlist("keyPoints")
    api_key = request.form.get("apiKey", "").strip()

    preferences = {
        "subject": subject,
        "hours": hours,
        "days": days,
        "keyPoints": keyPoints,
        "apiKey": api_key
    }
=======
    keyPoints = request.form.getlist("keyPointsList")
    preferences = {"subject": subject, "hours": hours, "days": days, "keyPoints": keyPoints}
>>>>>>> a29b327d24e5bd98af073c5b5452339f2f837249

    result = main_workflow(preferences)
    return render_template(
        "result.html", study_plan=result["study_plan"], tasks=result["tasks"]
    )


if __name__ == "__main__":
    app.run(debug=True)