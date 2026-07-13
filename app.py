import os
import concurrent.futures
os.environ["OPENCV_AVFOUNDATION_SKIP_AUTH"] = "1"

# Thread pool for YOLO inference — keeps Flask responsive during heavy computation
_yolo_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

from graph import generate_bar_graph
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_file,
    Response,
    jsonify,
    session,
    send_from_directory
)
from flasgger import Swagger
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import datetime

from detector import detect_animals
from report import generate_pdf
from webcam import generate_frames, model
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

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Animal Detection API",
        "description": "API for detecting animals in images using AI",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Format: Bearer <token>"
        }
    },
    "security": [{"Bearer": []}],
    "consumes": ["application/json", "multipart/form-data"],
    "produces": ["application/json"]
}

swagger = Swagger(app, template=swagger_template)

app.secret_key = "AnimalDetectionSecretKey123"

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JWT_SECRET_KEY"] = "AnimalDetectionJWTSecretKey123"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

@app.route("/uploads/<filename>")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ---- JWT Error Handlers — return clean messages instead of raw HTTP codes ----

@jwt.unauthorized_loader
def missing_token_callback(reason):
    return jsonify({"success": False, "message": "Authentication required. Please log in and provide a valid token."}), 401

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return jsonify({"success": False, "message": "Authentication failed. Invalid token provided."}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "message": "Authentication failed. Your session has expired. Please log in again."}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "message": "Authentication failed. Token has been revoked."}), 401

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("access_token_cookie")
    if not token:
        token = request.cookies.get("refresh_token_cookie")
        
    if token:
        from database import is_access_token_revoked, get_refresh_token
        # Check AccessTokens table
        if is_access_token_revoked(token):
            return True
        # Check RefreshTokens table
        ref_record = get_refresh_token(token)
        if ref_record and ref_record["IsRevoked"]:
            return True
            
    return False


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
        username=session.get("user", "")
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
# Standard route removed, we rely on API endpoints now.


# ---------------- HISTORY PAGE ----------------

@app.route("/history")
def history_page():
    return render_template("history.html", username="")

# ---------------- WEBCAM ----------------

@app.route("/webcam")
def webcam():
    return render_template(
        "index.html",
        detections=None,
        animal_count=None,
        summary=None,
        webcam=True,
        username=""
    )


# ---------------- LIVE VIDEO ----------------

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

# COCO class IDs for all animals (excluding 0=person)
# 14=bird, 15=cat, 16=dog, 17=horse, 18=sheep,
# 19=cow, 20=elephant, 21=bear, 22=zebra, 23=giraffe
ANIMAL_CLASSES = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@app.route("/api/detect_frame", methods=["POST"])
@jwt_required()
def api_detect_frame():
    import numpy as np
    import cv2

    file = request.files.get("image")
    if not file:
        return jsonify({"success": False, "message": "Missing image file"}), 400

    file_bytes = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"success": False, "message": "Invalid image format"}), 400

    h, w = frame.shape[:2]

    # Run YOLO on GPU thread — returns raw results, NOT an annotated image
    def _run_yolo(f):
        return model.predict(
            source=f,
            conf=0.40,
            classes=ANIMAL_CLASSES,
            verbose=False
        )

    results = _yolo_executor.submit(_run_yolo, frame).result()

    # Return only bounding box coordinates + labels as JSON (~200 bytes vs ~50KB JPEG)
    boxes = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        label = model.names[int(box.cls[0])]
        boxes.append({
            "x1": round(x1 / w, 4),
            "y1": round(y1 / h, 4),
            "x2": round(x2 / w, 4),
            "y2": round(y2 / h, 4),
            "conf": round(float(box.conf[0]), 2),
            "label": label
        })

    return jsonify({"success": True, "boxes": boxes})

# ---------------- DOWNLOAD CSV ----------------

@app.route("/download_csv")
def download_csv():
    if os.path.exists("results.csv"):
        return send_file("results.csv", as_attachment=True)
    return "No CSV file found."


# ---------------- DOWNLOAD PDF ----------------

@app.route("/download_pdf")
def download_pdf():
    if not os.path.exists("results.csv"):
        return "Run animal detection first."

    generate_pdf()
    return send_file("Animal_Report.pdf", as_attachment=True)


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
        user_id = get_user_id(user)

        from database import get_active_refresh_token, save_refresh_token, save_access_token
        
        # Check if there is an active, unexpired, unrevoked refresh token
        active_rt = get_active_refresh_token(user_id)
        if active_rt:
            refresh_token = active_rt["TokenHash"]
        else:
            refresh_token = create_refresh_token(identity=str(user))
            refresh_expires = app.config["JWT_REFRESH_TOKEN_EXPIRES"]
            expiry_date = datetime.datetime.now() + refresh_expires
            save_refresh_token(user_id, refresh_token, expiry_date)

        access_token = create_access_token(identity=str(user))
        
        # Save access token in database
        access_expires = app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        access_expiry_date = datetime.datetime.now() + access_expires
        save_access_token(user_id, access_token, access_expiry_date)

        from flask_jwt_extended import set_access_cookies, set_refresh_cookies
        response = jsonify({
            "success": True,
            "message": "Login successful.",
            "token": access_token,
            "refresh_token": refresh_token,
            "username": user
        })
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200

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
    summary: Logout a user and revoke their refresh token
    security:
      - Bearer: []
    responses:
      200:
        description: Logged out successfully
    """
    # Extract access token
    auth_header = request.headers.get("Authorization", "")
    access_token = None
    if auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
    if not access_token:
        access_token = request.cookies.get("access_token_cookie")

    # Extract refresh token
    refresh_token = None
    if request.is_json:
        data = request.get_json(silent=True) or {}
        refresh_token = data.get("refresh_token")
    if not refresh_token:
        refresh_token = request.cookies.get("refresh_token_cookie")

    from database import get_refresh_token, revoke_refresh_token, revoke_access_token

    if access_token:
        revoke_access_token(access_token)

    if refresh_token:
        token_record = get_refresh_token(refresh_token)
        if token_record:
            revoke_refresh_token(token_record["Id"])

    session.pop("user", None)
    from flask_jwt_extended import unset_jwt_cookies
    response = jsonify({
        "success": True,
        "message": "Logged out successfully."
    })
    unset_jwt_cookies(response)
    return response, 200


@app.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def api_refresh():
    """
    Refresh Access Token
    ---
    tags:
      - Authentication
    summary: Refresh JWT access token using a refresh token
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed successfully
      401:
        description: Invalid, expired, or revoked refresh token
      403:
        description: Security warning (reuse detected)
    """
    username = get_jwt_identity()
    user_id = get_user_id(username)

    auth_header = request.headers.get("Authorization", "")
    raw_token = None
    if auth_header.startswith("Bearer "):
        raw_token = auth_header.split(" ")[1]

    if not raw_token:
        raw_token = request.cookies.get("refresh_token_cookie")

    if not raw_token:
        return jsonify({
            "success": False,
            "message": "Missing refresh token."
        }), 401

    from database import get_refresh_token, save_access_token

    token_record = get_refresh_token(raw_token)

    if not token_record:
        return jsonify({
            "success": False,
            "message": "Invalid refresh token."
        }), 401

    if token_record["IsRevoked"]:
        return jsonify({
            "success": False,
            "message": "Refresh token has been revoked."
        }), 401

    expiry = token_record["ExpiryDate"]
    if isinstance(expiry, str):
        try:
            expiry = datetime.datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

    if expiry < datetime.datetime.now():
        return jsonify({
            "success": False,
            "message": "Refresh token has expired."
        }), 401

    # Create new access token
    new_access_token = create_access_token(identity=str(username))
    
    # Save access token in database
    access_expires = app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    access_expiry_date = datetime.datetime.now() + access_expires
    save_access_token(user_id, new_access_token, access_expiry_date)

    from flask_jwt_extended import set_access_cookies, set_refresh_cookies
    response = jsonify({
        "success": True,
        "token": new_access_token,
        "refresh_token": raw_token
    })
    set_access_cookies(response, new_access_token)
    set_refresh_cookies(response, raw_token)
    return response, 200
@app.route("/api/upload", methods=["POST"])
@jwt_required()
def api_upload():
    """
    Upload Images
    ---
    tags:
      - Images
    summary: Upload one or more images.
    consumes:
      - multipart/form-data
    security:
      - Bearer: []
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
        description: Missing or invalid token.
    """
    files = request.files.getlist("images")

    if not files:
        return jsonify({
            "success": False,
            "message": "No images uploaded."
        }), 400

    current_user = get_jwt_identity()
    user_id = get_user_id(current_user)

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
@jwt_required()
def api_detect():
    """
    Detect Animals
    ---
    tags:
      - Detection
    summary: Run YOLO detection.
    security:
      - Bearer: []
    responses:
      200:
        description: Detection completed.
      400:
        description: No uploaded images found.
      401:
        description: Missing or invalid token.
    """
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
@jwt_required()
def api_history():
    """
    Upload History
    ---
    tags:
      - Images
    summary: View uploaded image history for the current user.
    security:
      - Bearer: []
    responses:
      200:
        description: Upload history.
      401:
        description: Missing or invalid token.
    """
    current_user = get_jwt_identity()
    user_id = get_user_id(current_user)

    history = get_upload_history(user_id)

    return jsonify(history), 200

@app.route("/api/history", methods=["DELETE"])
@jwt_required()
def api_clear_history():
    """
    Clear All History
    ---
    tags:
      - Images
    summary: Delete all uploaded images and detection results for the current user.
    security:
      - Bearer: []
    responses:
      200:
        description: History cleared.
      401:
        description: Missing or invalid token.
    """
    current_user = get_jwt_identity()
    user_id = get_user_id(current_user)

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
@jwt_required()
def api_profile():
    """
    User Profile
    ---
    tags:
      - User
    summary: Get current user's profile.
    security:
      - Bearer: []
    responses:
      200:
        description: User details.
      401:
        description: Missing or invalid token.
    """
    current_user = get_jwt_identity()
    profile = get_user_profile(current_user)

    return jsonify(profile), 200

@app.route("/api/image/<int:image_id>", methods=["DELETE"])
@jwt_required()
def api_delete_image(image_id):
    """
    Delete Image
    ---
    tags:
      - Images
    summary: Delete uploaded image (must belong to the current user).
    security:
      - Bearer: []
    parameters:
      - in: path
        name: image_id
        type: integer
        required: true
    responses:
      200:
        description: Image deleted.
      401:
        description: Missing or invalid token.
      404:
        description: Image not found or not owned by this user.
    """
    current_user = get_jwt_identity()
    user_id = get_user_id(current_user)

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
    import cv2
    print("[INIT] Initializing camera from the main thread to check macOS permissions...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("[INIT] Camera opened successfully from the main thread.")
        cap.release()
    else:
        print("[WARNING] Camera could not be opened at startup.")

    app.run(debug=True, port=8000, threaded=True)
