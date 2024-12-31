from flask import Flask, request, render_template
from study_assistant import main_workflow  # Import your study assistant function

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")  # HTML form for user input


@app.route("/generate", methods=["POST"])
def generate():
    # Extract form data
    subject = request.form.get("subject", "").strip()  # Ensure default if missing
    hours = int(request.form.get("hours", 0))  # Default to 0 if missing
    days = int(request.form.get("days", 0))  # Default to 0 if missing

    # Build the preferences dictionary
    preferences = {"subject": subject, "hours": hours, "days": days}

    # Pass preferences to main_workflow
    result = main_workflow(preferences)

    # Render the result page
    return render_template("result.html", study_plan=result["study_plan"], tasks=result["tasks"])


if __name__ == "__main__":
    app.run(debug=True)
