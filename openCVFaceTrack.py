import cv2

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
            center_x = x + w // 2
            center_y = y + h // 2
        
            if center_x < 200:
                print('Move left')
            elif center_x > 440:
                print('Move right')
            if center_y < 120:
                print('Move up')
            elif center_y > 360:
                print('Move down')
        
        cv2.imshow('frame', frame)
    
        if cv2.waitKey(1) == ord('q'):
            break
        
cap.release()
cv2.destroyAllWindows()

