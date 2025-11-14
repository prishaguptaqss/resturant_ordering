import subprocess
import uuid
import os
from fastapi import UploadFile

UPLOAD_DIR = "uploads"
CONVERTED_DIR = "converted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)


async def process_audio(file: UploadFile):
    """Save m4a file → convert to wav → delete original"""
    
    input_filename = f"{UPLOAD_DIR}/{uuid.uuid4()}.m4a"
    output_filename = f"{CONVERTED_DIR}/{uuid.uuid4()}.wav"

    # Save uploaded file
    with open(input_filename, "wb") as buffer:
        buffer.write(await file.read())

    # Convert to WAV
    cmd = [
        "ffmpeg",
        "-i", input_filename,
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        output_filename
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Delete original file
    try:
        os.remove(input_filename)
    except Exception as e:
        print(f"Warning: Failed to delete {input_filename}: {e}")

    return output_filename
