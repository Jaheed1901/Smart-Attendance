"""
Configuration File
Project: Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition
Ramdeobaba University - IDEA Lab (2026-27)
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATA_DIR = os.path.join(BASE_DIR, "data")
STUDENTS_DIR = os.path.join(DATA_DIR, "students")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
MANUAL_REVIEWS_DIR = os.path.join(DATA_DIR, "manual_reviews")
EVAL_RESULTS_DIR = os.path.join(BASE_DIR, "evaluation", "results")
EVAL_PLOTS_DIR = os.path.join(BASE_DIR, "evaluation", "plots")

# Ensure required directories exist
for directory in [DATABASE_DIR, DATA_DIR, STUDENTS_DIR, EMBEDDINGS_DIR, MANUAL_REVIEWS_DIR, EVAL_RESULTS_DIR, EVAL_PLOTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database Configuration
DATABASE_PATH = os.environ.get("GATE_DATABASE_PATH", os.path.join(DATABASE_DIR, "attendance.db"))

# Biometric & Model Storage
EMBEDDINGS_FILE = os.path.join(EMBEDDINGS_DIR, "enrolled_embeddings.npy")
EMBEDDINGS_METADATA_FILE = os.path.join(EMBEDDINGS_DIR, "enrolled_metadata.json")

# =========================================================================
# Camera & Video Stream Settings (Continuous 120 FPS High-Speed Monitoring)
# =========================================================================
CAMERA_INDEX = int(os.environ.get("GATE_CAMERA_INDEX", 0))  # Default webcam index
CAMERA_WIDTH = 640                # Capture frame width
CAMERA_HEIGHT = 480               # Capture frame height
CAMERA_FPS = 120                  # Target FPS (120 FPS continuous high-speed monitoring)
FPS_TARGET = 120                  # High-speed capture target
FRAME_SKIP = 1                    # Process recognition on frames (smooth tracking)
CONTINUOUS_MONITORING = True      # Continuous monitoring during operating hours
AUTO_START_CAMERA = True          # Automatically start camera hardware on startup
CAMERA_MODE = "AUTO"              # 'AUTO' (bidirectional), 'ENTRY', or 'EXIT'

# Face Detection & Tracking Configuration
DETECTOR_BACKEND = os.environ.get("GATE_DETECTOR_BACKEND", "auto")  # 'auto', 'insightface', or 'opencv'
FACE_DETECTION_SIZE = (640, 640)  # Input dimension for RetinaFace / SCRFD
MIN_FACE_SIZE = 40                # Minimum pixel dimension (w, h)
DETECTION_CONFIDENCE_MIN = 0.50   # Minimum detector score
TRACKER_MAX_DISAPPEARED = 15      # Frames a face can be missing before drop
TRACKER_IOU_THRESHOLD = 0.35      # IoU threshold for spatial tracking

# =========================================================================
# Confidence-Aware Decision Thresholds (Cosine Similarity & Margin)
# Cosine similarity range is [-1.0, 1.0]. Genuine ArcFace matches: [0.45, 0.90]
# =========================================================================
COSINE_ACCEPT_THRESHOLD = float(os.environ.get("GATE_ACCEPT_THRESHOLD", 0.50))
COSINE_REJECT_THRESHOLD = float(os.environ.get("GATE_REJECT_THRESHOLD", 0.35))
COSINE_MARGIN_MIN = float(os.environ.get("GATE_MARGIN_MIN", 0.08))

# Backward compatibility aliases
HIGH_CONFIDENCE_THRESHOLD = COSINE_ACCEPT_THRESHOLD
UNCERTAIN_THRESHOLD = COSINE_REJECT_THRESHOLD

# Multi-frame Aggregation Configuration
MULTI_FRAME_ENABLED = os.environ.get("GATE_MULTI_FRAME", "true").lower() in ("true", "1", "yes")
TRACK_BUFFER_MAX_FRAMES = 5       # Accumulate top quality frames per track
TRACK_MIN_FRAMES_DECISION = 2     # Minimum accumulated frames before track-level decision

# Face Quality Gate
QUALITY_GATE_ENABLED = True
BLUR_THRESHOLD = float(os.environ.get("GATE_BLUR_THRESHOLD", 40.0))  # Laplacian variance threshold
MAX_POSE_YAW = 45.0               # Degrees

# Anti-Spoofing & Liveness Check (Motion & Mandatory Eye Blink Verification)
SPOOF_CHECK_ENABLED = True
SPOOF_MOTION_MIN = 0.8            # Minimum inter-frame motion energy to pass
MIN_CENTROID_DISPLACEMENT = 3.0   # Minimum spatial displacement in pixels across frames (steady person blocked)
REQUIRE_EYE_BLINK = True          # Prevent photo/video screen proxy via mandatory eye blink verification
MIN_BLINKS_FOR_ATTENDANCE = 1     # Person MUST blink eyes at least once to be marked present
MAX_FRAMES_WITHOUT_BLINK = 35     # Flag static presentation if no blink detected after N frames
MAX_FRAMES_STEADY_PROXY = 20      # Steady person without blink for 20 frames is flagged as PROXY ATTEMPT
PHONE_SCREEN_DETECTION_ENABLED = True # Optical texture & specular glare detection for phone screen photos
PHONE_SPECULAR_GLARE_RATIO = 0.05 # Fraction of pixels in specular glare range characteristic of glass phone displays

# Doorway Division & Directional Gate Lanes
DOORWAY_DIVISION_ENABLED = True
DOORWAY_SPLIT_RATIO = 0.50        # Frame split ratio: 0.50 = 50% (x = 320 for 640px)
ENTRY_LANE_NAME = "ENTRY"         # Left side of doorway
EXIT_LANE_NAME = "EXIT"           # Right side of doorway

# Enrollment Configuration
ENROLLMENT_SAMPLES_COUNT = 3      # Number of face snapshots captured per student
ENROLLMENT_SIMILARITY_MIN = 0.40  # Minimum consistency between captured sample embeddings
REQUIRE_STUDENT_CONSENT = True    # Explicit student biometric consent flag required

# Data Protection & Privacy Configuration
ENCRYPTION_ENABLED = True         # Encrypt embeddings and biometric logs at rest
RETENTION_DAYS = 30               # Auto-retention days for crop images and reviews

# =========================================================================
# Timetable, Early Arrival & Temporary Exit Configuration
# =========================================================================
TIMETABLE_CSV = os.path.join(DATA_DIR, "timetable.csv")
DEFAULT_SECTION = "V A"
DEFAULT_BATCH = "ALL"
DEFAULT_SUBJECT = "Idea Lab"
DEFAULT_ROOM = "DT-403"
DEFAULT_SESSION_DURATION = 3600   # 1 hour in seconds
ENTRY_WINDOW_BEFORE_MINS = 30     # Early arrival window allowed before class (e.g. 30 mins)
ENTRY_WINDOW_LATE_MINS = 15       # Late entry window after start time (marked LATE)
AUTO_TIMETABLE_SYNC = True        # Automatically create & manage sessions from schedule

# Break & Washroom Attendance Rules
MAX_SINGLE_BREAK_MINS = 15.0          # Max duration for a single temporary exit before review flag
MAX_CUMULATIVE_OUTSIDE_MINS = 20.0    # Max total time outside during lecture
MIN_CLASSROOM_PRESENCE_PERCENT = 75.0 # Required presence percentage to be marked present (e.g. 75%)
DEBOUNCE_SECONDS = 4.0                # Debounce window preventing duplicate events from repeated frames
MAX_DUPLICATE_INTERVAL = 300          # 5 minutes cooldown per tracker

# Mock Institutional App Sync Configuration (Mock Juno Interface)
MOCK_JUNO_ENABLED = True
MOCK_JUNO_ENDPOINT = "http://127.0.0.1:5000/api/juno/sync"
MOCK_JUNO_API_KEY = "JUNO-RAMDEOBABA-CSE-2026-KEY"
MOCK_JUNO_FAILURE_RATE = float(os.environ.get("GATE_MOCK_FAILURE_RATE", 0.0))
MOCK_JUNO_LATENCY_MS = int(os.environ.get("GATE_MOCK_LATENCY_MS", 0))

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
DEBUG_MODE = False
