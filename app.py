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
    # Retrieve content from the form
    study_plan = request.form.get("study_plan", "No study plan available.")
    tasks = request.form.get("tasks", "No tasks available.")

    # Combine content into a single string
    file_content = f"Your Study Plan\n\n{study_plan}\n\nDetailed Daily Study Tasks\n\n{tasks}"

    # Create an in-memory text file
    output = io.BytesIO()
    output.write(file_content.encode("utf-8"))
    output.seek(0)

    # Serve the file as a download
    return send_file(output, as_attachment=True, download_name="study_plan.txt", mimetype="text/plain")


@app.route("/generate", methods=["GET", "POST"])
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