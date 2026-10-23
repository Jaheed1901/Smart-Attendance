"""
Main Web Server & Application Entrypoint
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)
"""

import os
import time
import threading
import base64
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, send_from_directory

import config
from database.database import init_db
from recognition.recognizer import FaceRecognizer
from recognition.camera_monitor import CameraHealthMonitor
from enrollment.enroll import StudentEnrollmentManager
from attendance.session import AttendanceSessionManager
from attendance.timetable import TimetableManager
from attendance.attendance import AttendanceManager
from api.routes import api_bp, init_api

# Initialize Flask Application
app = Flask(
    __name__,
    template_folder=os.path.join(config.BASE_DIR, "dashboard", "templates"),
    static_folder=os.path.join(config.BASE_DIR, "dashboard", "static")
)

# Global Component Singletons
print("[INIT] Initializing Database Schema...")
init_db()

print("[INIT] Initializing Face Recognizer Engine...")
recognizer = FaceRecognizer(
    backend=config.DETECTOR_BACKEND,
    t_accept=config.COSINE_ACCEPT_THRESHOLD,
    t_reject=config.COSINE_REJECT_THRESHOLD,
    m_min=config.COSINE_MARGIN_MIN
)

print("[INIT] Initializing Timetable & Attendance Managers...")
enrollment_manager = StudentEnrollmentManager(recognizer.detector, recognizer.embedding_manager)
session_manager = AttendanceSessionManager()
timetable_manager = TimetableManager()
attendance_manager = AttendanceManager()

# Camera Health Monitor Failure Hook
def on_camera_hardware_failure(reason: str):
    active = session_manager.get_active_session()
    if active:
        session_manager.mark_monitoring_incomplete(active["id"], reason)
        print(f"[ALERT] Session #{active['id']} marked MONITORING_INCOMPLETE: {reason}")

camera_monitor = CameraHealthMonitor(on_failure_cb=on_camera_hardware_failure)

# Threaded Camera Controller with 60 FPS & Clean Hardware ON/OFF
class CameraStream:
    def __init__(self, src=config.CAMERA_INDEX, monitor=None):
        self.src = src
        self.monitor = monitor
        self.cap = None
        self.grabbed = False
        self.frame = None
        self.is_camera_on = False  # Default state: OFF unless auto-started
        self.camera_mode = "AUTO"  # Options: 'AUTO', 'ENTRY', 'EXIT'
        self.running = True
        self.read_lock = threading.Lock()

        # Background capture worker thread
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

        # Optional auto-start
        if config.AUTO_START_CAMERA:
            try:
                self.start_camera()
            except Exception as e:
                print(f"[WARN] Auto-start camera could not acquire device: {e}")

    def set_camera_mode(self, mode: str):
        mode_clean = mode.upper()
        if mode_clean in ("AUTO", "ENTRY", "EXIT"):
            self.camera_mode = mode_clean
            return True
        return False

    def start_camera(self):
        with self.read_lock:
            if self.is_camera_on and self.cap and self.cap.isOpened():
                return True, "Camera is already running"

            try:
                # Open DirectShow on Windows for fastest device acquisition
                self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.src)

                if not self.cap.isOpened():
                    self.is_camera_on = False
                    return False, f"Could not access webcam at index {self.src}. Ensure it is connected and not in use."

                # Set FOURCC to MJPG for high-speed 120 FPS camera streaming capability
                try:
                    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                except Exception:
                    pass

                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

                # Warm up camera sensor
                for _ in range(3):
                    self.grabbed, self.frame = self.cap.read()
                    time.sleep(0.02)

                self.is_camera_on = True
                print(f"[INFO] Camera {self.src} opened at {config.CAMERA_FPS} FPS.")
                return True, f"Camera hardware opened successfully ({config.CAMERA_FPS} FPS)"
            except Exception as e:
                self.is_camera_on = False
                return False, f"Failed to initialize webcam: {e}"

    def stop_camera(self):
        with self.read_lock:
            self.is_camera_on = False
            if self.cap:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
            self.grabbed = False
            self.frame = None
            print("[INFO] Camera hardware released successfully.")
            return True, "Camera stopped and hardware released"

    def _capture_loop(self):
        # Target 120 FPS high-speed capture interval
        sleep_interval = 1.0 / (config.CAMERA_FPS * 1.5)
        while self.running:
            if self.is_camera_on and self.cap and self.cap.isOpened():
                grabbed, frame = self.cap.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
                if self.monitor:
                    self.monitor.inspect_frame(frame, grabbed)
                time.sleep(sleep_interval)
            else:
                time.sleep(0.05)

    def read(self):
        with self.read_lock:
            if self.is_camera_on and self.frame is not None:
                return self.grabbed, self.frame.copy()
            return False, None

camera_stream = CameraStream(src=config.CAMERA_INDEX, monitor=camera_monitor)

# Background Timetable Auto-Sync Thread
def _timetable_background_sync_worker():
    while True:
        try:
            if config.AUTO_TIMETABLE_SYNC:
                session_manager.auto_sync_with_timetable(timetable_manager, room=config.DEFAULT_ROOM)
        except Exception as e:
            pass
        time.sleep(30)

sync_thread = threading.Thread(target=_timetable_background_sync_worker, daemon=True)
sync_thread.start()

# Link all managers with REST API router
init_api(
    recognizer=recognizer,
    enrollment=enrollment_manager,
    session_mgr=session_manager,
    attendance_mgr=attendance_manager,
    timetable_mgr=timetable_manager,
    camera_stream=camera_stream,
    camera_monitor=camera_monitor
)
app.register_blueprint(api_bp)

def generate_video_stream():
    """
    Yields multipart JPEG frames.
    When camera is OFF, renders high-contrast standby slate with clear status.
    When camera is ON, runs face recognition pipeline with 60 FPS HUD overlays.
    """
    frame_idx = 0
    cached_annotated = None

    while True:
        if not camera_stream.is_camera_on:
            # Standby Card: White Institutional Slate
            standby = np.full((480, 640, 3), 248, dtype=np.uint8)
            cv2.rectangle(standby, (20, 20), (620, 460), (255, 255, 255), -1)
            cv2.rectangle(standby, (20, 20), (620, 460), (220, 225, 230), 2)

            cv2.putText(standby, "RAMDEOBABA UNIVERSITY - IDEA LAB", (40, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 41, 59), 2)
            cv2.putText(standby, "Smart Gate-Entry Multi-Face Attendance System", (40, 175),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 116, 139), 1)

            cv2.rectangle(standby, (40, 210), (340, 250), (241, 245, 249), -1)
            cv2.rectangle(standby, (40, 210), (340, 250), (203, 213, 225), 1)
            cv2.putText(standby, "CAMERA STATUS: OFF", (55, 236),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (220, 38, 38), 2)

            cv2.putText(standby, "Click [START CAMERA] on the dashboard to begin live recognition.", (40, 290),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (71, 85, 105), 1)
            cv2.putText(standby, f"Gate Room: {config.DEFAULT_ROOM}  |  Target FPS: {config.CAMERA_FPS}", (40, 330),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (148, 163, 184), 1)
            cv2.putText(standby, f"System Time: {time.strftime('%Y-%m-%d %H:%M:%S')}", (40, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (148, 163, 184), 1)

            ret, buffer = cv2.imencode(".jpg", standby, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            time.sleep(0.12)
            continue

        # Camera is ON
        grabbed, raw_frame = camera_stream.read()

        if not grabbed or raw_frame is None:
            time.sleep(0.015)
            continue

        frame_idx += 1
        active_session = session_manager.get_active_session()
        active_id = active_session["id"] if active_session else None
        active_room = active_session.get("room", config.DEFAULT_ROOM) if active_session else config.DEFAULT_ROOM

        # Attendance callback hooks connected to continuous gate & exit tracking with Doorway Lane Division
        def on_present_cb(session_id, student_id, roll_number, name, section, similarity_score, margin=None, decision_rule="TOP1_AND_MARGIN", room="DT-403", lane=None):
            event_type = lane if (camera_stream.camera_mode == "AUTO" and lane) else camera_stream.camera_mode
            is_new, msg, status_after = attendance_manager.process_gate_detection(
                session_id=session_id,
                student_id=student_id,
                roll_number=roll_number,
                name=name,
                section=section,
                similarity_score=similarity_score,
                margin=margin,
                decision_rule=decision_rule,
                event_type=event_type,
                camera_id=f"GATE-CAM-01-{event_type}",
                room=room
            )
            return is_new

        def on_uncertain_cb(session_id, temp_track_id, face_image_path, candidate_student_id,
                            candidate_roll_number, candidate_name, similarity_score, margin=None,
                            top_k_candidates=None, room="DT-403"):
            attendance_manager.add_to_manual_review(
                session_id=session_id,
                temp_track_id=temp_track_id,
                face_image_path=face_image_path,
                candidate_student_id=candidate_student_id,
                candidate_roll_number=candidate_roll_number,
                candidate_name=candidate_name,
                similarity_score=similarity_score,
                margin=margin,
                top_k_candidates=top_k_candidates,
                room=room,
                camera_id=f"GATE-CAM-01-{camera_stream.camera_mode}"
            )

        def on_proxy_cb(session_id, student_id, roll_number, name, section, spoof_type, face_image_path=None, similarity_score=None, margin=None, room="DT-403"):
            attendance_manager.record_proxy_attempt(
                session_id=session_id,
                student_id=student_id,
                roll_number=roll_number,
                name=name,
                section=section,
                spoof_type=spoof_type,
                similarity_score=similarity_score,
                margin=margin,
                face_image_path=face_image_path,
                room=room
            )

        if frame_idx % config.FRAME_SKIP == 0 or cached_annotated is None:
            annotated, events = recognizer.process_frame(
                raw_frame,
                active_session_id=active_id,
                room=active_room,
                on_present=on_present_cb,
                on_uncertain=on_uncertain_cb,
                on_proxy_detected=on_proxy_cb
            )

            # Draw camera operational mode & 120 FPS high-speed badge overlay on top left
            cv2.rectangle(annotated, (10, 10), (240, 42), (255, 255, 255), -1)
            cv2.rectangle(annotated, (10, 10), (240, 42), (200, 210, 220), 1)
            cv2.putText(annotated, f"MODE: {camera_stream.camera_mode} | 120 FPS", (18, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (30, 41, 59), 2)

            cached_annotated = annotated
        else:
            annotated = cached_annotated

        ret, buffer = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
        if not ret:
            continue

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
        time.sleep(0.008)

# Dashboard Routes
@app.route("/")
@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

@app.route("/video_feed")
def video_feed():
    return Response(
        generate_video_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/api/camera/snapshot")
def get_camera_snapshot():
    """Returns snapshot for enrollment preview without Windows device lock conflicts."""
    grabbed, raw_frame = camera_stream.read()
    if not grabbed or raw_frame is None:
        if not camera_stream.is_camera_on:
            camera_stream.start_camera()
            time.sleep(0.2)
            grabbed, raw_frame = camera_stream.read()

    if not grabbed or raw_frame is None:
        return jsonify({"success": False, "message": "Camera frame not available. Please click START CAMERA."}), 503

    ret, buffer = cv2.imencode(".jpg", raw_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
    if not ret:
        return jsonify({"success": False, "message": "Encoding error"}), 500

    b64_str = "data:image/jpeg;base64," + base64.b64encode(buffer.tobytes()).decode("utf-8")
    return jsonify({"success": True, "image": b64_str}), 200

if __name__ == "__main__":
    print("=" * 65)
    print(" RAMDEOBABA UNIVERSITY - IDEA LAB (2026-27)")
    print(" Smart Gate-Entry Attendance System with Confidence-Aware Recognition")
    print(f" Continuous Monitoring at 60 FPS | Server: http://127.0.0.1:{config.SERVER_PORT}")
    print("=" * 65)
    app.run(
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        debug=config.DEBUG_MODE,
        threaded=True
    )
