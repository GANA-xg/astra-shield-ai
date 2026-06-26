import whisper

model = whisper.load_model("base")

result = model.transcribe("../data/samples/sample.wav")

print(result["text"])