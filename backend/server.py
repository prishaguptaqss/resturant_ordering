from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
from contextlib import asynccontextmanager
from helper import process_audio, validate_audio
from whisper_manager import whisper_manager, transcribe_audio
import time
from test import parser

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
        
        # ✅ VALIDATE AUDIO BEFORE PROCESSING
        is_valid, error_msg, audio_info = validate_audio(wav_path)
        if not is_valid:
            print(f"❌ Audio validation failed: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "audio_info": audio_info
            }
        
        print(f"✅ Audio valid: {audio_info['duration']:.2f}s, max_level: {audio_info['max_level']:.3f}")
        
        # Transcribe
        start = time.time()
        transcription = transcribe_audio(wav_path)
        elapsed = time.time() - start
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        print(f"✅ {elapsed:.2f}s: {transcription}")
        
        # Parse order
        try:
            start_time = time.time()
            order_result = parser.parse_order(transcription)
            processing_time = time.time() - start_time
            
            response = {
                "status": "success",
                "transcription": transcription,
                "transcription_time_seconds": round(elapsed, 2),
                "order": {
                    "items": order_result["items"],
                    "summary": {
                        "total_items": order_result["items_count"],
                        "total_value": order_result["total_order_value"],
                        "currency": order_result["currency"],
                        "confidence": order_result["confidence"]
                    },
                    "original_text": order_result["original_text"],
                    "parsing_time_seconds": round(processing_time, 2)
                },
                "audio_info": audio_info
            }
            
            if "error" in order_result:
                response["order"]["error"] = order_result["error"]
                
            return response
            
        except Exception as e:
            return {
                "status": "error",
                "transcription": transcription,
                "error": f"Order parsing failed: {str(e)}",
                "transcription_time_seconds": round(elapsed, 2),
                "audio_info": audio_info
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
