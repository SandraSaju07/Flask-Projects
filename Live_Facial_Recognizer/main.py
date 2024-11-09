import face_recognition  # type: ignore
import cv2  # type: ignore
import numpy as np
from flask import Flask, render_template, Response, redirect, url_for

app = Flask(__name__)
video_capture = None  # Initialize the video capture object to None

# Load sample pictures and learn how to recognize them
obama_image = face_recognition.load_image_file("./pics/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

michelle_image = face_recognition.load_image_file("./pics/michelle.jpg")
michelle_face_encoding = face_recognition.face_encodings(michelle_image)[0]

zendaya_image = face_recognition.load_image_file('./pics/zendaya.jpg')
zendaya_face_encoding = face_recognition.face_encodings(zendaya_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    michelle_face_encoding,
    zendaya_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Michelle Obama",
    "Zendaya Coleman"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def generate_frames():
    global process_this_frame, face_locations, face_encodings, face_names, video_capture

    while video_capture.isOpened():

        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            break

        # Only process every other frame of video to save time
        if process_this_frame:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                else:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html',camera_state=video_capture is not None and video_capture.isOpened())

@app.route('/start')
def start_video():
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)  # Start the video capture
    return redirect(url_for('index'))

@app.route('/stop')
def stop_video():
    global video_capture
    if video_capture is not None and video_capture.isOpened():
        video_capture.release()  # Stop the video capture
    return redirect(url_for('index'))

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
