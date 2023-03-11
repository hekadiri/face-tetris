import cv2

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
delay = 10
frame_count=0

while True:
    ret, frame = cap.read()
    
    if frame is not None:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Draw box around middle of the video feed
        box_thickness = 2
        box_color = (255, 0, 0) # Blue color
        frame_height, frame_width, _ = frame.shape
        box_height = frame_height // 2 -450# Bit taller than half the frame height
        box_width = box_height +25 # Square box
        box_y = (frame_height - box_height) // 2
        box_x = (frame_width - box_width) // 2

        # Draw the box bounds of the middle of the video feed
        cv2.rectangle(frame, (box_x, box_y), (box_x+box_width-1, box_y+box_height-1), box_color, box_thickness)
        
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
            # Find the largest face
        max_area = 0
        max_face = None
        for (x, y, w, h) in faces:
            if w*h > max_area:
                max_area = w*h
                max_face = (x, y, w, h)
        
        # Track only the largest face
        if max_face is not None:
            x, y, w, h = max_face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Draws the rectangle around the face
        
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            if frame_count >= delay:
                if face_center_x < box_x:
                    frame_count=0
                    print('Move right')
                elif face_center_x > box_x + box_width:
                    frame_count=0
                    print('Move left')
                elif face_center_y < box_y:
                    frame_count=0
                    print('Move up')
                elif face_center_y > box_y + box_height:
                    frame_count=0
                    print('Move down')
            else:
                frame_count += 1
        
        # Flip the frame horizontally
        flipped_frame = cv2.flip(frame, 1)
        cv2.imshow('frame', flipped_frame)
    
        if cv2.waitKey(1) == ord('q'):
            break
        
cap.release()
cv2.destroyAllWindows()
