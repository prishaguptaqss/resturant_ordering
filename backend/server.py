from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from contextlib import asynccontextmanager
from helper import process_audio
from whisper_manager import whisper_manager, transcribe_audio
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup"""
    print(" Starting server...")
    whisper_manager.start_server(model="base", hw_arch="hailo8l")
    print("✅ Ready!")
    yield
    whisper_manager.stop_server()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": whisper_manager.initialized
    }


@app.post("/audio")
async def receive_audio(file: UploadFile = File(...)):
    try:
        # Convert audio
        wav_path = await process_audio(file)
        
        # Transcribe
        start = time.time()
        transcription = transcribe_audio(wav_path)
        elapsed = time.time() - start
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        print(f"✅ {elapsed:.2f}s: {transcription}")
        
        return {
            "status": "success",
            "transcription": transcription,
            "time_seconds": round(elapsed, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
