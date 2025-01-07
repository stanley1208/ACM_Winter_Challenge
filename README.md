# ACM_Winter_Challenge
## Introduction
The Study Assistant project is a web-based tool designed to help users create personalized learning plans. Users can input their study topic, daily study time, number of study days, and key points of focus. Powered by an integrated ChatGPT-4o model, the tool generates a unique study plan tailored to the user's inputs.

Each plan includes:
- Detailed task descriptions
- Estimated study time
- Study key points
- Recommended learning resources (books, websites, videos, etc.)

The platform also offers a convenient download feature, allowing users to save their study plans locally for future reference.

This project is ideal for anyone looking for a structured and efficient approach to achieving their learning goals.
## How to use
- Requirement library
```python
flask
python >= 3.7
```
- Steps to activate this program
```python
# Assume you have installed the anaconda environment
conda create --name studyassist
conda activate studyassist
cd /path/ACM_Winter_Challenge
python app.py
# Access it through http://127.0.0.1:5000/ on your local browser
```