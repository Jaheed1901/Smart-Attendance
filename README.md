# Smart Gate-Entry Attendance System with Confidence-Aware Multi-Face Recognition and Mock Institutional App Integration

**Department of Computer Science & Engineering / AIML | IDEA Lab (Session 2026-27)**  
**Ramdeobaba University, Nagpur, India**

---

### Project Members
- **Swara Bhandwalkar**, Roll No. 60 / 61 (Section V A, Batch A4)
- **Aryan Dixit**, Roll No. 21 (Section V A, Batch A2)
- **Pushkar Kolhe**, Roll No. 51 (Section V A, Batch A4)
- **Jaheed Pathan**, Roll No. 53 (Section V A, Batch A4)
- **Arpit Kadwe**, Roll No. 55 (Section V A, Batch A4)

**Project Guide:** Prof. Dhanshree Junghare  
**Timetable In-Charge:** Prof. N. Lanke | **Associate Head:** Dr. R. Welekar | **Dean & Head, CSE:** Dr. P. D. Adane

---

## 1. Executive Summary & Problem Formulation
Manual attendance methods in university classrooms (e.g., paper roll-calls, sign-in sheets) waste 7–12 minutes per lecture, enable proxy attendance, and create administrative delays. Standard commercial face recognition solutions frequently fail under realistic university gate conditions:
1. They force non-enrolled students onto the nearest enrolled identity (closed-set assumption).
2. They collapse recognition into a single misleading "confidence %" score rather than analyzing top-1 cosine similarity alongside separation margin to the second-best candidate.
3. They spam duplicate attendance records across consecutive video frames.
4. They lack fault tolerance against camera disconnects, tampering, or network outages.
5. They do not synchronize with the university class timetable or cloud ERPs (e.g. Juno).

This repository delivers a complete, production-grade prototype deployed at the classroom gate. It incorporates:
* **Dual-Criteria Decision Rules:** Top-1 Cosine Similarity ($s_1 \ge T_{accept}$) **AND** Margin ($s_1 - s_2 \ge M_{min}$) to prevent lookalike misidentification.
* **Open-Set Rejection:** Non-enrolled persons strictly resolve to `REJECT (UNKNOWN)`.
* **Multi-Frame Temporal Aggregation:** Accumulates face embeddings across frames, computes the L2-normalized mean of highest-quality frames per track, with a single-frame toggle for baseline evaluation.
* **Face Quality Gating:** Rejects motion blur via Laplacian variance scoring and extreme pose angles.
* **Timetable Integration:** Synchronized with the Ramdeobaba University V Sem AIML Class Schedule (Rooms DT-403, DT-406, DT-612, DT-509, DT-609, etc.) with configurable early/late timing windows.
* **Faculty Review & Student Dispute Flow:** Side-by-side candidate comparison, one-click confirmation or reassignment, and student attendance dispute handling.
* **Hardware Resilience:** Camera health monitor with disconnect, freeze, and occlusion detection, automatic reconnect backoff, and durable SQLite offline buffering.
* **Biometric Privacy at Rest:** AES Fernet encryption of face embeddings, mandatory student consent verification, and automated 30-day crop retention purging.
* **Clean White Institutional UI:** Professional, user-friendly white background theme (`#ffffff` / `#f8fafc`) with dedicated `START CAMERA` / `STOP CAMERA` controls.

---

## 2. Decision Logic: Cosine Similarity & Margin Separation

Cosine similarity is bounded in $[-1.0, 1.0]$ and represents the inner product between two L2-normalized ArcFace vectors:
$$\text{Sim}(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^{512} u_i v_i$$
> [!IMPORTANT]
> Cosine similarity is a geometric distance metric, **not a probability**. It is never labeled or presented as a probability percentage in code, APIs, or the UI.

Let $s_1$ denote the highest cosine similarity in the enrolled gallery, and let $s_2$ denote the second-highest similarity (runner-up candidate). The margin is defined as:
$$\Delta s = s_1 - s_2$$

The system applies three mutually exclusive decision rules configured via environment variables / `config.py`:

```
                           [ LIVE FACE CROP ]
                                   │
                                   ▼
                        [ ARCFACE 512-D VECTOR ]
                                   │
                                   ▼
             [ COSINE SIMILARITY AGAINST ALL ENROLLED PROFILES ]
                        Sort: s1 >= s2 >= s3 ...
                                   │
                                   ▼
 ┌─────────────────────────────────┼─────────────────────────────────┐
 ▼                                 ▼                                 ▼
s1 < T_reject           s1 >= T_accept AND            Otherwise
(s1 < 0.35)             (s1 - s2) >= M_min            (Ambiguous Margin or
                        (s1 >= 0.50 & Δs >= 0.08)     Borderline Band)
 │                                 │                                 │
 ▼                                 ▼                                 ▼
REJECT                         AUTO_MARK                          REVIEW
• Open-Set Impostor            • Genuine Match Verified           • Divert to Review Queue
• Non-Enrolled Person          • Gate Entry Recorded              • Candidate Top-k Stored
• Never Forced onto Gallery    • Synced to Mock Juno Cloud        • Faculty Review Action
```

---

## 3. Technology Stack

| Layer | Component | Version / Specification |
|:---|:---|:---|
| **Programming Language** | Python | 3.12 (64-bit, Windows AMD64) |
| **Web Server & REST API** | Flask / Werkzeug | 3.0.3 (Threaded WSGI, Blueprint routing) |
| **Face Detection** | InsightFace SCRFD / RetinaFace | 2.0 (`buffalo_sc`, ONNX Runtime CPU) |
| **Feature Extraction** | ArcFace | 512-dimensional normalized embeddings |
| **Detection Quality Gate** | OpenCV | 5.0.0 (Laplacian blur variance check) |
| **Multi-Face Tracking** | Spatial IoU Tracker | Multi-frame temporal buffer (top-5 quality mean) |
| **Security & Privacy** | Cryptography & Bcrypt | AES Fernet at rest, Bcrypt password hashing |
| **Database** | SQLite 3 | WAL Mode (`PRAGMA journal_mode=WAL`), strict unique constraints |
| **Frontend Dashboard** | HTML5, CSS3, Vanilla JS | User-friendly white institutional theme (`#ffffff` / `#f8fafc`) |
| **Evaluation Suite** | NumPy, SciPy, Matplotlib | 3.11.2 (ROC curves, FAR/FRR, latency percentiles) |

---

## 4. University Timetable Schedule (Ramdeobaba V Sem AIML)

The system parses the schedule from `data/timetable.csv` (originating from the institutional timetable PDF):

| Day | Time Slot | Subject | Code | Room | Batch | Faculty |
|:---|:---|:---|:---|:---|:---|:---|
| **Monday** | 09:00 - 10:00 | Machine Learning (ML) | 24CS03TH0501 | DT-406 | ALL | Dr. A. Pimpalkar |
| **Monday** | 10:00 - 12:00 | ML Lab / DAV Lab | 24CS03PR0501/4 | DT-509/609 | A1-A4 | Dr. Pimpalkar / Prof. Meshram |
| **Monday** | 13:00 - 14:00 | Computer Networks (CN) | 24CS03TH0503 | DT-612 | ALL | Prof. N. Lanke |
| **Monday** | 14:00 - 16:00 | CN Lab / C&EC Lab | 24CS03PR0503/2 | DT-303/306 | A1-A4 | Prof. Lanke / Prof. Patil |
| **Tuesday**| 09:00 - 11:00 | **Idea Lab** | 24CS03PR0505 | **DT-403** | **ALL** | **Prof. S. Meshram / Prof. D. Junghare** |
| **Tuesday**| 13:00 - 14:00 | Machine Learning (ML) | 24CS03TH0501 | DT-403 | ALL | Dr. A. Pimpalkar |
| **Wednesday**| 10:00 - 11:00| PDA / IP | 24CS03TH0506 | DT-609/702 | ALL | Prof. Junghare / Prof. Meshram |
| **Thursday**| 13:00 - 14:00 | **Idea Lab** | 24CS03PR0505 | **DT-403** | **ALL** | **Prof. S. Meshram / Prof. D. Junghare** |
| **Friday** | 11:00 - 12:00 | Cloud & Edge Computing | 24CS03TH0502 | DT-403 | ALL | Prof. H. Patil |
| **Friday** | 13:00 - 14:00 | Computer Networks (CN) | 24CS03TH0503 | DT-403 | ALL | Prof. N. Lanke |

### Timing Windows:
* **Early Window:** $\le 15$ minutes before start time $\implies$ tagged `EARLY`.
* **On-Time Window:** Start time up to $+15$ minutes late margin $\implies$ tagged `ON_TIME`.
* **Late Arrival:** $> 15$ minutes after start time $\implies$ tagged `LATE`.
* **Outside Schedule:** $\implies$ tagged `UNASSIGNED` (never attached to a guessed class).
* **Room Conflict Detection:** If multiple lectures overlap in the same room, a room conflict is flagged and automatic assignment is suspended.

---

## 5. Camera Mounting & Hardware Deployment Guidelines

To achieve consistent recognition at classroom doorways with a standard low-cost USB webcam, adhere to these deployment specifications:

```
                  ┌────────────────────────┐
                  │   GATE CAMERA MOUNT    │
                  └───────────┬────────────┘
                              │ Height: 2.1m - 2.3m
                              │ Tilt: 15° - 20° downward
                              ▼
        ┌─────────────────────────────────────────────────┐
        │                                                 │
        │                                                 │
Doorway │                CAPTURE ZONE                     │
════════╡           Distance: 1.8m - 3.2m                 │
        │           Face Size: >= 80x80 px                │
        │                                                 │
        └─────────────────────────────────────────────────┘
```

1. **Mounting Height:** $2.1\text{ m} - 2.3\text{ m}$ ($6.9\text{ ft} - 7.5\text{ ft}$) above finished floor level. Mount centrally above the entrance doorframe.
2. **Mounting Angle:** Tilt camera downward by $15^\circ - 20^\circ$. This captures approaching students with an optimal frontal pitch angle ($< 15^\circ$) while minimizing occlusion from hair or hats.
3. **Capture Zone (Distance):** $1.8\text{ m} - 3.2\text{ m}$ from the doorway. At this distance, a standard $640\times 480$ sensor yields faces larger than $80\times 80$ pixels, easily exceeding the minimum quality gate ($40\times 40$ pixels).
4. **Illumination & Lighting:**
   * Provide diffuse overhead LED lighting ($400 - 600\text{ lux}$) in the doorway corridor.
   * **Avoid Backlighting:** Never mount the camera facing external open windows or glass doors where sunlight backlights entering students, causing facial silhouettes.
   * Maintain consistent color temperature ($4000\text{K} - 5000\text{K}$ neutral white).

---

## 6. Biometric Privacy, Security & Data Protection

The system is engineered in accordance with Indian Digital Personal Data Protection (DPDP) principles:
1. **Mandatory Student Consent:** Enrollment requires the explicit `consent_given=1` flag. Without consent, no facial embedding is generated or saved.
2. **AES Fernet Encryption at Rest:** All 512-dimensional embedding vectors stored in the SQLite database are encrypted at rest using AES-128-CBC with HMAC authentication (`cryptography.fernet`). The encryption key is loaded from the environment variable `GATE_FERNET_KEY` or a protected local keyfile.
3. **Privacy-Preserving Public APIs:** Public and dashboard REST endpoints never leak raw 512-dimensional embedding vectors or uncropped frames.
4. **Automated 30-Day Retention Policy:** Run `python cleanup_retention.py` (or schedule via cron / Windows Task Scheduler) to automatically purge face crops and resolved review logs older than 30 days:
   ```bash
   python cleanup_retention.py --days 30
   ```
5. **Role-Based Access Control (RBAC):** Distinct roles (`ADMIN`, `FACULTY`, `STUDENT`) with Bcrypt password hashing ($12$ rounds salt). Initial admin account can be provisioned via CLI:
   ```bash
   python manage_users.py create_admin -u admin -p "SecureAdmin@2026" -n "Dean Admin"
   ```

---

## 7. Installation, Setup & Running

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database and Seed Students
```bash
python seed_database.py
```
This initializes the schema and populates the 60 students for Section V A, along with default admin credentials (`admin` / `Admin@123`).

### Step 3: Run the Application Server
```bash
python app.py
```
Open your browser at **`http://127.0.0.1:5000`** to access the dashboard.

### Step 4: Run the Automated Unit Test Suite
```bash
python -m unittest tests/test_system.py
```
All 13 unit tests will execute and verify database constraints, decision rules, quality gates, timetable matching, dispute handling, camera monitoring, and offline queueing.

### Step 5: Run the Scientific Evaluation Suite
```bash
python evaluation/evaluate.py
```
Generates ROC curves, similarity distributions, latency percentiles ($p50, p95$), and FPS benchmarks across $N \in [1, 10, 30, 60]$ enrolled students into `evaluation/plots/` and `evaluation/results/evaluation_results.csv`.

---

## 8. Open-Source Licenses & Attribution

This project is built using free, open-source software libraries:
* **InsightFace / ArcFace:** Deep face recognition library licensed under the MIT / Apache 2.0 License.
* **OpenCV (`opencv-python`):** Open Source Computer Vision Library licensed under the Apache 2.0 License.
* **Flask:** Lightweight WSGI web framework licensed under the BSD 3-Clause License.
* **Cryptography:** Python cryptographic primitives licensed under the Apache 2.0 / BSD License.
* **Bcrypt:** Modern password hashing library licensed under the Apache 2.0 License.
* **SQLite:** Public domain transactional database engine.
* **NumPy / SciPy / Matplotlib:** Scientific computation and plotting libraries licensed under BSD / PSF licenses.
