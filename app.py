from flask import Flask, jsonify, request
import cv2
import datetime
import os

app = Flask(__name__)

API_KEY = os.getenv("SNAPSHOT_API_KEY", "supersecret123")
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "snapshots")
LOG_FILE = os.getenv("SECURITY_LOG_FILE", "security.log")


def _client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def write_access_log(*, success: bool, status_code: int, reason: str) -> None:
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_line = (
        f"{timestamp} | ip={_client_ip()} | endpoint=/snapshot | "
        f"status={status_code} | success={success} | reason={reason}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(log_line)


@app.route("/health", methods=["GET"])
def health() -> tuple:
    return jsonify({"status": "ok"}), 200


@app.route("/snapshot", methods=["GET"])
def take_snapshot() -> tuple:
    user_key = request.args.get("key") or request.headers.get("X-API-Key")
    if user_key != API_KEY:
        write_access_log(success=False, status_code=403, reason="unauthorized")
        return jsonify({"error": "Unauthorized"}), 403

    cap = None
    try:
        cap = cv2.VideoCapture(0)
        if not cap or not cap.isOpened():
            write_access_log(success=False, status_code=500, reason="camera_not_opened")
            return jsonify({"error": "Camera access failed"}), 500

        ret, frame = cap.read()
        if not ret:
            write_access_log(success=False, status_code=500, reason="camera_read_failed")
            return jsonify({"error": "Camera capture failed"}), 500

        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        filename = f"security_shot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)
        saved = cv2.imwrite(filepath, frame)

        if not saved:
            write_access_log(success=False, status_code=500, reason="image_write_failed")
            return jsonify({"error": "Image write failed"}), 500

        write_access_log(success=True, status_code=200, reason="snapshot_saved")
        return jsonify(
            {
                "message": "Snapshot saved!",
                "status": "success",
                "file": filepath,
            }
        ), 200
    except Exception as exc:
        write_access_log(success=False, status_code=500, reason=f"exception:{type(exc).__name__}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if cap is not None:
            cap.release()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
