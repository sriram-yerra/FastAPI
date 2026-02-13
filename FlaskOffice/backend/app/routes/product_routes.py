from flask import Blueprint, request, jsonify, send_file
from app.database import get_session
from app.models.user_model import User, EmailOTP
from app.models.product_model import Detections
from app.dependancies import get_current_user
from app.schemas.user_schema import CreateUser, OTPVerify, UpdateUser, loginUser, UserRead, Token
from app.auth import hash_password, verified_password, create_acess_token
from app.emailverfication import send_otp_email, generate_otp
from ultralytics import YOLO
import cv2, numpy as np, os
import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename

router = Blueprint('product_routes', __name__)

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

MODEL_PATH = os.path.join(BASE_DIR, "weights", "combined_best.pt")

IMG_SAVE_DIR = os.path.join(BASE_DIR, "storage", "images")
VID_SAVE_DIR = os.path.join(BASE_DIR, "storage", "videos")

os.makedirs(IMG_SAVE_DIR, exist_ok=True)
os.makedirs(VID_SAVE_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

def detect_image(image_bytes):
    start = time.time()

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    results = model(img)

    annotated = results[0].plot()
    inference_time = (time.time() - start) * 1000
    boxes = results[0].boxes
    num_detections = len(boxes)
    classes = [model.names[int(cls)] for cls in boxes.cls]
    confidence_avg = float(boxes.conf.mean()) if num_detections > 0 else 0.0

    metadata = {
        "inference_time_ms": inference_time,
        "num_detections": num_detections,
        "classes_detected": ",".join(classes),
        "confidence_avg": confidence_avg,
    }
    return annotated, metadata

def save_image(image, file_name):
    name, ext = os.path.splitext(file_name)
    filename = f"{name}_result.jpg"
    filepath = os.path.join(IMG_SAVE_DIR, filename)
    cv2.imwrite(filepath, image)
    return filename, filepath   # return only filename

IMG_EXT = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg"]

@router.route("/view-image", methods=["GET"])
@get_current_user
def view_image(current_user=None, session=None):
    path = request.args.get('path')
    if not path:
        return jsonify({"detail": "Path parameter required"}), 400
    
    try:
        return send_file(path, mimetype="image/jpeg")
    finally:
        if session:
            session.close()

@router.route("/detect-image", methods=["POST"])
@get_current_user
def detect(current_user=None, session=None):
    try:
        if 'file' not in request.files:
            return jsonify({"detail": "No file provided"}), 400
        
        file = request.files['file']
        custom_file_name = request.args.get('custom_file_name')
        
        if file.filename == '':
            return jsonify({"detail": "No file selected"}), 400

        image_bytes = file.read()

        name, ext = os.path.splitext(file.filename)
        ext = ext.lower()

        if ext not in IMG_EXT:
            return jsonify({"detail": "Only image files allowed"}), 400

        annotated, meta = detect_image(image_bytes)
        image_name = name
        
        if custom_file_name:
            object_name, file_path = save_image(annotated, custom_file_name)
        else:
            object_name, file_path = save_image(annotated, image_name)

        total_detections = meta["num_detections"]

        record = Detections(
            filename=object_name,
            filepath=file_path,
            inference_time_ms=meta["inference_time_ms"],
            num_detections=meta["num_detections"],
            classes_detected=meta["classes_detected"],
            confidence_avg=meta["confidence_avg"],
        )

        session.add(record)
        session.commit()

        return jsonify({
            "message": "Detections done",
            "download_url": f"{file_path}",
            "Total Detections": f"{total_detections}",
        }), 200
    finally:
        if session:
            session.close()

@router.route("/detections", methods=["GET"])
def get_detections():
    file_name = request.args.get('file_name')
    file_id = request.args.get('file_id', type=int)
    
    session = next(get_session())
    try:
        if file_id is not None:
            record = session.query(Detections).filter(Detections.id == file_id).first()
            if not record:
                return jsonify({"detail": "Detection not found"}), 404
            return jsonify({
                "id": record.id,
                "filename": record.filename,
                "filepath": record.filepath,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "inference_time_ms": record.inference_time_ms,
                "num_detections": record.num_detections,
                "classes_detected": record.classes_detected,
                "confidence_avg": record.confidence_avg
            }), 200

        if file_name is not None:
            records = session.query(Detections).filter(Detections.filename == file_name).all()
            return jsonify([{
                "id": r.id,
                "filename": r.filename,
                "filepath": r.filepath,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                "inference_time_ms": r.inference_time_ms,
                "num_detections": r.num_detections,
                "classes_detected": r.classes_detected,
                "confidence_avg": r.confidence_avg
            } for r in records]), 200

        records = session.query(Detections).all()
        return jsonify([{
            "id": r.id,
            "filename": r.filename,
            "filepath": r.filepath,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            "inference_time_ms": r.inference_time_ms,
            "num_detections": r.num_detections,
            "classes_detected": r.classes_detected,
            "confidence_avg": r.confidence_avg
        } for r in records]), 200
    finally:
        session.close()

@router.route("/download", methods=["GET"])
@get_current_user
def download_file(current_user=None, session=None):
    try:
        file_name = request.args.get('file_name')
        file_id = request.args.get('file_id', type=int)
        
        if not file_name and not file_id:
            return jsonify({"detail": "Provide file_id or file_name"}), 400

        if file_name:
            record = session.query(Detections).filter(Detections.filename == file_name).first()
        else:
            record = session.query(Detections).filter(Detections.id == file_id).first()

        if not record:
            return jsonify({"detail": "Record not found"}), 404

        path = record.filepath

        if not os.path.exists(path):
            return jsonify({"detail": "File missing on server"}), 404

        return send_file(
            path,
            mimetype="image/jpeg",
            as_attachment=True,
            download_name=record.filename
        )
    finally:
        if session:
            session.close()

@router.route("/detections/all", methods=["DELETE"])
@get_current_user
def delete_all_detections(current_user=None, session=None):
    try:
        records = session.query(Detections).all()

        for rec in records:
            if os.path.exists(rec.filepath):
                os.remove(rec.filepath)   # delete image file too
            session.delete(rec)

        session.commit()
        return jsonify({"message": "All detections cleared"}), 200
    finally:
        if session:
            session.close()

@router.route("/detections/id/<int:file_id>", methods=["DELETE"])
@get_current_user
def delete_by_id(file_id, current_user=None, session=None):
    try:
        record = session.query(Detections).filter(Detections.id == file_id).first()

        if not record:
            return jsonify({"detail": "Detection not found"}), 404

        if os.path.exists(record.filepath):
            os.remove(record.filepath)

        session.delete(record)
        session.commit()

        return jsonify({"message": f"Detection {file_id} deleted"}), 200
    finally:
        if session:
            session.close()

@router.route("/detections-history", methods=["GET"])
@get_current_user
def detections_history(current_user=None, session=None):
    try:
        records = session.query(Detections).order_by(Detections.id.desc()).all()

        return jsonify([
            {
                "id": r.id,
                "filename": r.filename,
                "filepath": r.filepath,
                "num_detections": r.num_detections,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in records]
        ), 200
    finally:
        if session:
            session.close()
