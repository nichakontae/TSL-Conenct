from ultralytics import YOLO

model = YOLO("extend_modelv22.pt")
model.export(format="onnx")
