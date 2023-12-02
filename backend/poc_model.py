import onnxruntime as ort

model = ort.InferenceSession("sub.onnx", providers=['CPUExecutionProvider'])
inputs = model.get_inputs()

input = inputs[0]
print("Name:", input.name)
print("Type:", input.type)
print("Shape:", input.shape)
