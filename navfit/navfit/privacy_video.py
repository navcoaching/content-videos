"""Face blur for REAL footage (path A), robust to profile views and fast motion.

Per frame, the head box comes from the best available source:
  1. MediaPipe face detection (frontal / 3/4 faces)
  2. MediaPipe pose landmarks (nose, eyes, ears) — works in profile and when the
     face detector misses because of motion blur
  3. Fallback: last known box, expanded while it is stale (never "unblurred")
A constant-velocity smoother follows the head between frames. Frames where the
head was only extrapolated are listed in the report so they can be checked.

Rule: if no box was ever found before a frame, the WHOLE upper third of the frame
is blurred rather than risking an exposed face.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request

import cv2
import numpy as np

MODELS = {
    "face": ("https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/"
             "blaze_face_short_range.tflite", "blaze_face_short_range.tflite"),
    "pose": ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/1/"
             "pose_landmarker_full.task", "pose_landmarker_full.task"),
}


def _model(kind):
    url, name = MODELS[kind]
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "models")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    if not os.path.exists(p):
        urllib.request.urlretrieve(url, p)
    return p


def _ffmpeg():
    import shutil
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def blur_video(src, dst, debug=False, strength=0.18):
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision

    face = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=_model("face")), running_mode=vision.RunningMode.VIDEO,
        min_detection_confidence=0.35))
    pose = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=_model("pose")), running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.4, min_tracking_confidence=0.4))

    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    tmp = dst + ".video.mp4"
    enc = subprocess.Popen([_ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                            "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", tmp],
                           stdin=subprocess.PIPE)
    state = None  # (cx, cy, r, vx, vy)
    stale = 0
    report = {"frames": 0, "face": 0, "pose": 0, "extrapolated": [], "fullblur": []}
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        ts = int(i * 1000 / fps)
        rgb = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        box, src_kind = None, None
        fr = face.detect_for_video(rgb, ts)
        if fr.detections:
            d = max(fr.detections, key=lambda d: d.categories[0].score)
            b = d.bounding_box
            box = (b.origin_x + b.width / 2, b.origin_y + b.height / 2, max(b.width, b.height) * 0.75)
            src_kind = "face"
        pr = pose.detect_for_video(rgb, ts)
        if pr.pose_landmarks:
            lm = pr.pose_landmarks[0]
            ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # nose, eyes, ears, mouth
            pts = np.array([(lm[k].x * W, lm[k].y * H) for k in ids if lm[k].visibility > 0.3])
            if len(pts) >= 2:
                c = pts.mean(0)
                span = np.ptp(pts, axis=0).max()
                sh = np.array([(lm[k].x * W, lm[k].y * H) for k in (11, 12)])
                shoulder_w = np.linalg.norm(sh[0] - sh[1])
                r = max(span * 0.9, shoulder_w * 0.38, 18)
                pbox = (c[0], c[1] - r * 0.1, r)
                if box is None:
                    box, src_kind = pbox, "pose"
                else:  # union keeps both
                    box = ((box[0] + pbox[0]) / 2, (box[1] + pbox[1]) / 2, max(box[2], pbox[2], np.hypot(box[0] - pbox[0], box[1] - pbox[1]) + min(box[2], pbox[2])))
        if box is not None:
            if state is None:
                state = [box[0], box[1], box[2], 0.0, 0.0]
            else:
                a = 0.6
                vx, vy = box[0] - state[0], box[1] - state[1]
                state = [state[0] + a * vx, state[1] + a * vy, max(box[2], state[2] * 0.9 + box[2] * 0.1),
                         0.5 * state[3] + 0.5 * vx, 0.5 * state[4] + 0.5 * vy]
            stale = 0
            report[src_kind] += 1
        elif state is not None:
            stale += 1
            state = [state[0] + state[3], state[1] + state[4], state[2] * (1 + 0.08 * min(stale, 10)), state[3], state[4]]
            report["extrapolated"].append(i)
        if state is None:
            frame[: H // 3] = cv2.GaussianBlur(frame[: H // 3], (0, 0), 25)
            report["fullblur"].append(i)
        else:
            cx, cy, r = state[0], state[1], state[2] * (1 + strength)
            _blur_circle(frame, cx, cy, r)
            if debug:
                cv2.circle(frame, (int(cx), int(cy)), int(r), (0, 255, 0) if stale == 0 else (0, 0, 255), 2)
        enc.stdin.write(frame.tobytes())
        report["frames"] += 1
        i += 1
    enc.stdin.close()
    enc.wait()
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", tmp, "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "copy",
                    "-c:a", "aac", "-shortest", dst], check=True)
    os.remove(tmp)
    with open(dst + ".privacy.json", "w") as fh:
        json.dump(report, fh, indent=1)
    print(f"[blur] {dst}: {report['frames']} frames, face={report['face']} pose={report['pose']} "
          f"extrapolated={len(report['extrapolated'])} fullblur={len(report['fullblur'])}")
    return report


def _blur_circle(img, cx, cy, r):
    H, W = img.shape[:2]
    x0, x1 = int(max(0, cx - r * 1.4)), int(min(W, cx + r * 1.4))
    y0, y1 = int(max(0, cy - r * 1.4)), int(min(H, cy + r * 1.4))
    if x1 <= x0 or y1 <= y0:
        return
    roi = img[y0:y1, x0:x1]
    blk = max(4, int(r / 6))
    small = cv2.resize(roi, (max(1, roi.shape[1] // blk), max(1, roi.shape[0] // blk)), interpolation=cv2.INTER_AREA)
    pix = cv2.resize(small, (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_LINEAR)
    pix = cv2.GaussianBlur(pix, (0, 0), max(3, r / 5))
    m = np.zeros(roi.shape[:2], np.float32)
    cv2.circle(m, (int(cx - x0), int(cy - y0)), int(r), 1.0, -1)
    m = cv2.GaussianBlur(m, (0, 0), max(2, r * 0.1))[..., None]
    img[y0:y1, x0:x1] = (pix * m + roi * (1 - m)).astype(np.uint8)
