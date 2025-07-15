import cv2
import mediapipe as mp
import numpy as np
import pygame
import time
import pyttsx3
import json
import os

# === Text-to-speech ===
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# === MediaPipe FaceMesh ===
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# === Pygame Fullscreen Setup ===
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
font = pygame.font.Font(None, 48)

ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM<⎚ "]
KEYS = [list(row) for row in ROWS]
selected_text = ""

# === Calibration Storage ===
calib_file = "nose_full_calibration.json"
calib = {"left": None, "right": None, "up": None, "down": None}

def draw_keyboard(nose_x, nose_y, typed_text):
    screen.fill((255, 255, 255))
    key_width = WIDTH // 10
    key_height = HEIGHT // 5
    highlight_row, highlight_col = None, None

    text_surface = font.render("Typed: " + typed_text, True, (0, 0, 255))
    screen.blit(text_surface, (50, 20))

    for r, row in enumerate(KEYS):
        for c, key in enumerate(row):
            x = c * key_width + 10
            y = r * key_height + 100
            rect = pygame.Rect(x, y, key_width - 20, key_height - 20)

            if x <= nose_x <= x + key_width and y <= nose_y <= y + key_height:
                highlight_row, highlight_col = r, c
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)

            pygame.draw.rect(screen, color, rect, 3)
            label = font.render(key, True, color)
            screen.blit(label, (x + key_width // 4, y + key_height // 4))

    pygame.display.flip()
    return highlight_row, highlight_col

def euclidean(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def calibrate_nose(cap):
    steps = [("left", "Look LEFT and press SPACE"),
             ("right", "Look RIGHT and press SPACE"),
             ("up", "Look UP and press SPACE"),
             ("down", "Look DOWN and press SPACE")]

    for key, message in steps:
        while True:
            ret, frame = cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)
            h, w, _ = frame.shape

            if results.multi_face_landmarks:
                lm = results.multi_face_landmarks[0].landmark
                nose = lm[1]
                cx, cy = int(nose.x * w), int(nose.y * h)
                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                cv2.putText(frame, f"{key.upper()}: x={nose.x:.3f}, y={nose.y:.3f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            cv2.putText(frame, message, (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (100, 0, 200), 3)
            cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) & 0xFF == ord(' '):
                if results.multi_face_landmarks:
                    nose = results.multi_face_landmarks[0].landmark[1]
                    calib[key] = nose.x if key in ["left", "right"] else nose.y
                    print(f"Calibrated {key.upper()} = {calib[key]:.3f}")
                    break
    cv2.destroyWindow("Calibration")
    with open(calib_file, "w") as f:
        json.dump(calib, f)

# === Webcam + Calibration ===
cap = cv2.VideoCapture(0)
if os.path.exists(calib_file):
    with open(calib_file, "r") as f:
        calib = json.load(f)
else:
    calibrate_nose(cap)

last_select_time = time.time()
tap_cooldown = 1.0
mouth_open_threshold = 20

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)
    h, w, _ = frame.shape
    mapped_x, mapped_y = 0, 0

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        nose = lm[1]
        raw_x, raw_y = nose.x, nose.y

        # X-axis mapping
        if calib["left"] is not None and calib["right"] is not None:
            mapped_x = (raw_x - calib["left"]) / (calib["right"] - calib["left"]) * WIDTH
            mapped_x = int(np.clip(mapped_x, 0, WIDTH))
        else:
            mapped_x = int(raw_x * WIDTH)

        # Y-axis mapping
        if calib["up"] is not None and calib["down"] is not None:
            mapped_y = (raw_y - calib["up"]) / (calib["down"] - calib["up"]) * HEIGHT
            mapped_y = int(np.clip(mapped_y, 0, HEIGHT))
        else:
            mapped_y = int(raw_y * HEIGHT)

        # Draw feedback
        cv2.circle(frame, (int(nose.x * w), int(nose.y * h)), 5, (0, 255, 0), -1)

        # Mouth open check
        top_lip = (lm[13].x * w, lm[13].y * h)
        bottom_lip = (lm[14].x * w, lm[14].y * h)
        mouth_open = euclidean(top_lip, bottom_lip)
        cv2.putText(frame, f"Mouth: {mouth_open:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)

        # Draw & interact with keyboard
        row_idx, col_idx = draw_keyboard(mapped_x, mapped_y, selected_text)
        if mouth_open > mouth_open_threshold and (time.time() - last_select_time > tap_cooldown):
            if row_idx is not None and col_idx is not None:
                key = KEYS[row_idx][col_idx]
                if key == "<":
                    selected_text = selected_text[:-1]
                    speak("backspace")
                elif key == "⎚":
                    selected_text = ""
                    speak("cleared")
                elif key == " ":
                    selected_text += " "
                    speak("space")
                else:
                    selected_text += key
                    speak(key)
                last_select_time = time.time()
    else:
        draw_keyboard(0, 0, selected_text)

    cv2.imshow("Gaze Calibrated Input", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
