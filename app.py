from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    Response,
    session
)
from flasgger import Swagger

from detector import detect_animals
from report import generate_pdf
from webcam import generate_frames
from database import (
    register_user,
    login_user,
    get_user_id,
    save_uploaded_image
)

import os

app = Flask(__name__)
swagger = Swagger(app)

app.secret_key = "AnimalDetectionSecretKey123"

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- HOME ----------------

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        detections=None,
        animal_count=None,
        summary=None,
        webcam=False,
        username=session["user"]
    )


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        success = register_user(
            username,
            email,
            password
        )

        if success:
            return redirect("/login")

        return "Username or Email already exists."

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = login_user(
            username,
            password
        )

        if user:

            session["user"] = user

            return redirect("/")

        return "Invalid Username or Password."

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# ---------------- UPLOAD ----------------

# ---------------- UPLOAD ----------------

@app.route("/upload", methods=["POST"])
def upload():

    if "user" not in session:
        return redirect("/login")

    files = request.files.getlist("images")

    # Get the logged-in user's ID
    user_id = get_user_id(session["user"])

    for file in files:

        if file.filename != "":

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            # Save image details to MySQL
            save_uploaded_image(
                user_id,
                file.filename,
                filepath
            )

    return redirect("/")
# ---------------- DETECT ----------------

@app.route("/detect")
def detect():

    if "user" not in session:
        return redirect("/login")

    if not os.listdir(app.config["UPLOAD_FOLDER"]):
        return "Please upload one or more images before running detection."

    results = detect_animals("uploads")

    return render_template(
        "index.html",
        detections=results["detections"],
        animal_count=results["animal_count"],
        summary=results["summary"],
        webcam=False,
        username=session["user"]
    )


# ---------------- WEBCAM ----------------

@app.route("/webcam")
def webcam():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        detections=None,
        animal_count=None,
        summary=None,
        webcam=True,
        username=session["user"]
    )


# ---------------- LIVE VIDEO ----------------

@app.route("/video_feed")
def video_feed():

    if "user" not in session:
        return redirect("/login")

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# ---------------- DOWNLOAD CSV ----------------

@app.route("/download_csv")
def download_csv():

    if "user" not in session:
        return redirect("/login")

    if os.path.exists("results.csv"):

        return send_file(
            "results.csv",
            as_attachment=True
        )

    return "No CSV file found."


# ---------------- DOWNLOAD PDF ----------------

@app.route("/download_pdf")
def download_pdf():

    if "user" not in session:
        return redirect("/login")

    if not os.path.exists("results.csv"):

        return "Run animal detection first."

    generate_pdf()

    return send_file(
        "Animal_Report.pdf",
        as_attachment=True
    )


# ---------------- CLEAR SESSION ----------------

@app.route("/clear_session")
def clear_session():

    if "user" not in session:
        return redirect("/login")

    upload_folder = app.config["UPLOAD_FOLDER"]

    if os.path.exists(upload_folder):

        for filename in os.listdir(upload_folder):

            file_path = os.path.join(upload_folder, filename)

            if os.path.isfile(file_path):
                os.remove(file_path)

    if os.path.exists("results.csv"):
        os.remove("results.csv")

    if os.path.exists("Animal_Report.pdf"):
        os.remove("Animal_Report.pdf")

    return render_template(
        "index.html",
        detections=None,
        animal_count=None,
        summary=None,
        webcam=False,
        username=session["user"]
    )


# ---------------- RUN ----------------
# ---------------- TEST API ----------------

@app.route("/api/test", methods=["GET"])
def api_test():
    """
    Test API
    ---
    tags:
      - Testing
    summary: Test if Swagger is working.
    responses:
      200:
        description: Swagger is working.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Swagger is working!
    """

    return {
        "message": "Swagger is working!"
    }
if __name__ == "__main__":

    app.run(debug=True)