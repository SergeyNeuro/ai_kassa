from ultralytics import YOLO
import cv2
import numpy as np


class YoloPredicter:
    def __init__(self, model_name: str = "yolo11n.pt"):
        self.model = YOLO(model_name)

    async def predict(self, content):
        # Конвертация файла в изображение
        np_array = np.frombuffer(content, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        results = self.model(image)

        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            masks = result.masks  # Masks object for segmentation masks outputs
            keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            obb = result.obb  # Oriented boxes object for OBB outputs
            result.show()  # display to screen
            result.save(filename="result.jpg")  # save to disk
            print(boxes)
            print(masks)
            print(keypoints)
            print(probs)

