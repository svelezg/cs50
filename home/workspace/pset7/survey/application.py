import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__, static_url_path="", static_folder="")

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


# Check if all inputs are loaded (server-side)
@app.route("/form", methods=["POST"])
def post_form():
    # Renders error page
    if not request.form.get("name") or not request.form.get("lastname") or not request.form.get("email") or not request.form.get("degree"):
        return render_template("error.html", message="Please complete all required fields.")
    with open("survey.csv", "a") as file:
        writer = csv.DictWriter(file, fieldnames=["gender", "lastname", "name", "email", "degree"])
        writer.writerow({"gender": request.form.get("gender"), "lastname": request.form.get("lastname"), "name": request.form.get("name"),
                         "email": request.form.get("email"), "degree": request.form.get("degree")})
    # Redirects to sheet pagee
    return redirect("/sheet")


# Load registers table in sheet
@app.route("/sheet")
def get_sheet():
    with open("survey.csv", "r") as file:
        reader = csv.DictReader(file)
        registers = list(reader)
    return render_template("sheet.html", registers=registers)