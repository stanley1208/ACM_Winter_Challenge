from flask import Flask, request, render_template
from study_assistant import main_workflow  # Import your study assistant function

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")  # HTML form for user input


@app.route("/generate", methods=["POST"])
def generate():
    subject = request.form.get("subject", "").strip()
    hours = int(request.form.get("hours", 0))
    days = int(request.form.get("days", 0))
    preferences = {"subject": subject, "hours": hours, "days": days}

    result = main_workflow(preferences)
    print("DEBUG: Study Plan:", result["study_plan"])
    print("DEBUG: Tasks:", result["tasks"])  # Add this to check tasks content

    return render_template("result.html",
                           study_plan=result["study_plan"], tasks=result["tasks"])


if __name__ == "__main__":
    app.run(debug=True)
