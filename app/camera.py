import cv2
import numpy as np
#from Real_Time_Face_Recognition import Face_Recognition
import face_recognition
from app.models import User, DataBase
from app import db, app, login_manager
from flask_login import login_user, current_user, logout_user, login_required


@login_manager.user_loader
def load_user(login_id):
    return User.query.get(int(login_id))

def get_db():
	db = DataBase.query.all()
	db_face_encodings = list()
	db_name = list()
	db_user_id = list()
	for user in db:
		db_face_encodings.append(user.face_encoding())
		db_name.append(user.name)
		db_user_id.append(user.id)
	return (db_user_id,db_name, db_face_encodings)


	

class VideoCamera(object):
    def __init__(self, url):
       #capturing video
       self.url = url
       #print(self.url)
       self.stream = cv2.VideoCapture(self.url)
       #(self.grabbed, self.frame) = self.stream.read()
       #self.stopped = False
    def __del__(self):
        #releasing camera
        self.stream.release()

    def get_frame(self):
        ret, frame = self.stream.read()
        #print(frame)
        if frame is None:
            self.__del__()
            return None
        frame = cv2.resize(frame,(540,360))
        (db_user_id, db_names,db_face_encodings)=get_db()
        #print(db_user_id)
        unknown_face_locations = face_recognition.face_locations(frame)
        unknown_face_encodings = face_recognition.face_encodings(frame, unknown_face_locations)
        
        for (top, right, bottom, left), unknown_face_encoding in zip(unknown_face_locations, unknown_face_encodings):
            matches = face_recognition.compare_faces(db_face_encodings, unknown_face_encoding)
            name = "unknown"
            
            face_distances = face_recognition.face_distance(db_face_encodings, unknown_face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = db_names[best_match_index]
                face_id = db_user_id[best_match_index]
                data = DataBase.query.get_or_404(face_id)
                data.isPresent = 1
                db.session.commit()
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()















