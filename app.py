from graph import generate_bar_graph
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    Response,
    session,
    jsonify
)
from flasgger import Swagger

from detector import detect_animals
from report import generate_pdf
from webcam import generate_frames
from database import (
    register_user,
    login_user,
    get_user_id,
    save_uploaded_image,
    get_upload_history,
    get_detection_results,
    delete_uploaded_image,
    clear_upload_history,
    get_user_profile
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
        graph=None,
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
            image_id = save_uploaded_image(
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
    graph_path = generate_bar_graph(results["animal_count"])

    return render_template(
        "index.html",
        graph=graph_path,
        detections=results["detections"],
        animal_count=results["animal_count"],
        summary=results["summary"],
        webcam=False,
        username=session["user"]
    )


# ---------------- HISTORY PAGE ----------------

@app.route("/history")
def history_page():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "history.html",
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
        graph=None,
        detections=None,
        animal_count=None,
        summary=None,
        webcam=False,
        username=session["user"]
    )   
@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Register User
    ---
    tags:
      - Authentication
    summary: Register a new user
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Registration failed
    """

    data = request.get_json()

    success = register_user(
        data["username"],
        data["email"],
        data["password"]
    )

    if success:
        return jsonify({
            "success": True,
            "message": "User registered successfully."
        }), 201

    return jsonify({
        "success": False,
        "message": "Username or Email already exists."
    }), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Login User
    ---
    tags:
      - Authentication
    summary: Login a user
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """

    data = request.get_json()

    user = login_user(
        data["username"],
        data["password"]
    )

    if user:
        session["user"] = user

        return jsonify({
            "success": True,
            "message": "Login successful."
        }), 200

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401
@app.route("/api/logout", methods=["POST"])
def api_logout():
    """
    Logout User
    ---
    tags:
      - Authentication
    summary: Logout current user
    responses:
      200:
        description: Logout successful
    """

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })
@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Upload Images
    ---
    tags:
      - Images
    summary: Upload one or more images.
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: images
        type: file
        required: true
        description: Images to upload.
    responses:
      200:
        description: Images uploaded successfully.
      401:
        description: User not logged in.
    """

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    files = request.files.getlist("images")

    if not files:
        return jsonify({
            "success": False,
            "message": "No images uploaded."
        }), 400

    user_id = get_user_id(session["user"])

    uploaded = []

    for file in files:

        if file.filename != "":

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                file.filename
            )

            file.save(filepath)

            image_id = save_uploaded_image(
                user_id,
                file.filename,
                filepath
            )

            uploaded.append({
                "image_id": image_id,
                "filename": file.filename
            })

    return jsonify({
        "success": True,
        "uploaded": uploaded
    }), 200

@app.route("/api/detect", methods=["GET"])
def api_detect():
    """
    Detect Animals
    ---
    tags:
      - Detection
    summary: Run YOLO detection.
    responses:
      200:
        description: Detection completed.
      400:
        description: No uploaded images found.
    """

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    if not os.listdir(app.config["UPLOAD_FOLDER"]):
        return jsonify({
            "success": False,
            "message": "Upload images first."
        }), 400

    results = detect_animals("uploads")
    graph_path = generate_bar_graph(results["animal_count"])
    results["graph"] = graph_path

    return jsonify(results), 200

@app.route("/api/history", methods=["GET"])
def api_history():
    """
    Upload History
    ---
    tags:
      - Images
    summary: View uploaded image history for the current user.
    responses:
      200:
        description: Upload history.
      401:
        description: User not logged in.
    """

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = get_user_id(session["user"])

    history = get_upload_history(user_id)

    return jsonify(history), 200

@app.route("/api/history", methods=["DELETE"])
def api_clear_history():
    """
    Clear All History
    ---
    tags:
      - Images
    summary: Delete all uploaded images and detection results for the current user.
    responses:
      200:
        description: History cleared.
      401:
        description: User not logged in.
    """

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = get_user_id(session["user"])

    deleted = clear_upload_history(user_id)

    return jsonify({
        "success": True,
        "message": f"Cleared {deleted} history entries.",
        "deleted": deleted
    }), 200

@app.route("/api/results/<int:image_id>", methods=["GET"])
def api_results(image_id):
    """
    Detection Results
    ---
    tags:
      - Detection
    summary: Get detections of one image.
    parameters:
      - in: path
        name: image_id
        type: integer
        required: true
    responses:
      200:
        description: Detection results.
    """

    results = get_detection_results(image_id)

    return jsonify(results), 200

@app.route("/api/profile", methods=["GET"])
def api_profile():
    """
    User Profile
    ---
    tags:
      - User
    summary: Get current user's profile.
    responses:
      200:
        description: User details.
    """

    if "user" not in session:
        return jsonify({
            "success": False
        }), 401

    profile = get_user_profile(session["user"])

    return jsonify(profile), 200

@app.route("/api/image/<int:image_id>", methods=["DELETE"])
def api_delete_image(image_id):
    """
    Delete Image
    ---
    tags:
      - Images
    summary: Delete uploaded image (must belong to the current user).
    parameters:
      - in: path
        name: image_id
        type: integer
        required: true
    responses:
      200:
        description: Image deleted.
      401:
        description: User not logged in.
      404:
        description: Image not found or not owned by this user.
    """

    if "user" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = get_user_id(session["user"])

    deleted = delete_uploaded_image(image_id, user_id)

    if not deleted:
        return jsonify({
            "success": False,
            "message": "Image not found or you don't have permission to delete it."
        }), 404

    return jsonify({
        "success": True,
        "message": "Image deleted successfully."
    }), 200

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
@app.route("/download_graph")
def download_graph():

    graph_path = "static/graphs/animal_detection_graph.png"

    if os.path.exists(graph_path):

        return send_file(
            graph_path,
            as_attachment=True
        )

    return "No graph generated."
if __name__ == "__main__":
    app.run(debug=True, port=8000)
