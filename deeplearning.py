import cv2
from ultralytics import YOLO

LABEL_MAP = {
    0: "karnıyarık",        
    1: "ayran",             
    2: "domates çorbası",   
    3: "ezogelin çorbası",  
    4: "arnavut ciğeri",    
    5: "pizza",            
    6: "pilav",             
    7: "kola",             
    8: "salata",            
    9: "tatlı",             
    10: "muz",              
    11: "burger"            
}

def detect_yolov8(image, conf_thresh=0.5, fine_tuned=False):

    # Modeli sadece bir kez yükle
    if not hasattr(detect_yolov8, "model"):
        model_path = "yolov8.pt"
        detect_yolov8.model = YOLO(model_path)
        detect_yolov8.model_path = model_path
    else:
        current = getattr(detect_yolov8, "model_path", "")
        new = "yolov8.pt"
        if current != new:
            detect_yolov8.model = YOLO(new)
            detect_yolov8.model_path = new

    # BGR -> RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = detect_yolov8.model.predict(source=rgb, conf=conf_thresh, verbose=False)
    detected_classes = []
    for r in results:
        for box, conf, cls in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy(), r.boxes.cls.cpu().numpy()):
            detected_classes.append(int(cls))
            label_name = LABEL_MAP.get(int(cls), str(int(cls)))
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, label_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return image, detected_classes

