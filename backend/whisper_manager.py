import sys
import os
from threading import Lock
import queue

# Add Hailo path
sys.path.insert(0, "/home/qss/Hailo-Application-Code-Examples/runtime/hailo-8/python/speech_recognition")

# Import Hailo modules
from app.hailo_whisper_pipeline import HailoWhisperPipeline
from common.audio_utils import load_audio
from common.preprocessing import preprocess, improve_input_audio
from common.postprocessing import clean_transcription
from app.whisper_hef_registry import HEF_REGISTRY
import time
import atexit

def get_hef_path(model_variant: str, hw_arch: str, component: str) -> str:
    """Get HEF file path"""
    base_dir = "/home/qss/Hailo-Application-Code-Examples/runtime/hailo-8/python/speech_recognition"
    hef_path = HEF_REGISTRY[model_variant][hw_arch][component]
    
    if not os.path.isabs(hef_path):
        hef_path = os.path.join(base_dir, hef_path)
    
    if not os.path.exists(hef_path):
        raise FileNotFoundError(f"HEF file not found: {hef_path}")
    return hef_path

class WhisperManager:
    """
    Whisper Manager with Thread Lock
    
    KEY FEATURES:
    - Thread lock ensures ONE transcription at a time
    - Queue clearing prevents stale results
    - Request counter for debugging
    """
    
    _instance = None
    _pipeline = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhisperManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = False
            self.model = "base"
            self.hw_arch = "hailo8l"
            self._lock = Lock()  # ✅ THREAD LOCK
            self._request_counter = 0  # For debugging
    
    def start_server(self, model="base", hw_arch="hailo8l"):
        """Load the model once"""
        if self.initialized:
            print(f"✅ Model already loaded")
            return
        
        print(f"🚀 Loading Whisper model: {model} on {hw_arch}...")
        
        encoder_path = get_hef_path(model, hw_arch, "encoder")
        decoder_path = get_hef_path(model, hw_arch, "decoder")
        
        # Load model ONCE
        self._pipeline = HailoWhisperPipeline(
            encoder_path, 
            decoder_path, 
            model, 
            multi_process_service=False
        )
        
        self.model = model
        self.hw_arch = hw_arch
        self.chunk_length = 10 if "tiny" in model else 5
        self.initialized = True
        
        print(f"✅ Model loaded!")
        atexit.register(self.stop_server)
    
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe audio with thread lock and queue clearing
        
        CRITICAL WORKFLOW:
        1. Acquire lock (blocks other requests)
        2. Clear stale results from queue
        3. Process audio normally
        4. Release lock
        """
        if not self.initialized:
            raise Exception("Model not loaded. Call start_server() first.")
        
        # ✅ THREAD LOCK: Only one transcription at a time
        with self._lock:
            self._request_counter += 1
            request_id = self._request_counter
            
            try:
                print(f"\n🎤 Request #{request_id}: Processing {os.path.basename(audio_path)}")
                
                # ✅ CRITICAL: Clear stale results from pipeline queue
                cleared_count = 0
                while not self._pipeline.results_queue.empty():
                    try:
                        old_result = self._pipeline.results_queue.get_nowait()
                        cleared_count += 1
                    except queue.Empty:
                        break
                
                if cleared_count > 0:
                    print(f"   🗑️  Cleared {cleared_count} stale result(s) from queue")
                
                # Load audio
                sampled_audio = load_audio(audio_path)
                
                # Improve audio with VAD
                sampled_audio, start_time = improve_input_audio(sampled_audio, vad=True)
                chunk_offset = max(0, start_time - 0.2)
                
                # Preprocess into mel spectrograms
                mel_spectrograms = preprocess(
                    sampled_audio,
                    is_nhwc=True,
                    chunk_length=self.chunk_length,
                    chunk_offset=chunk_offset
                )
                
                num_chunks = len(mel_spectrograms)
                print(f"   📊 Processing {num_chunks} mel spectrogram chunks")
                
                # Send data to pipeline
                for mel in mel_spectrograms:
                    self._pipeline.send_data(mel)
                    time.sleep(0.1)
                
                # Get transcription (blocking call)
                transcription = self._pipeline.get_transcription()
                
                # Clean and return
                cleaned = clean_transcription(transcription)
                print(f"   ✅ Request #{request_id}: '{cleaned}'")
                
                return cleaned
                
            except Exception as e:
                print(f"   ❌ Request #{request_id} Error: {e}")
                import traceback
                traceback.print_exc()
                return None
    
    def stop_server(self):
        """Cleanup"""
        if self.initialized:
            self.initialized = False
            self._pipeline = None
            print("🛑 Model unloaded")

# Global instance
whisper_manager = WhisperManager()

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio using the global manager"""
    return whisper_manager.transcribe(audio_path)
