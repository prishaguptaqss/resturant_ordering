import sys
import os

# Add Hailo path so we can import their modules
sys.path.insert(0, "/home/qss/Hailo-Application-Code-Examples/runtime/hailo-8/python/speech_recognition")

# Import Hailo modules directly
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
    
    # Make path absolute if it's relative
    if not os.path.isabs(hef_path):
        hef_path = os.path.join(base_dir, hef_path)
    
    if not os.path.exists(hef_path):
        raise FileNotFoundError(f"HEF file not found: {hef_path}")
    return hef_path


class WhisperManager:
    """Keeps Hailo Whisper model loaded in memory"""
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
    
    def start_server(self, model="base", hw_arch="hailo8l"):
        """Load the model once"""
        if self.initialized:
            print(f"✅ Model already loaded")
            return
        
        print(f"🚀 Loading Whisper model: {model} on {hw_arch}...")
        
        # Get HEF paths
        encoder_path = get_hef_path(model, hw_arch, "encoder")
        decoder_path = get_hef_path(model, hw_arch, "decoder")
        
        # Load model ONCE
        self._pipeline = HailoWhisperPipeline(encoder_path, decoder_path, model, multi_process_service=False)
        
        self.model = model
        self.hw_arch = hw_arch
        self.chunk_length = 10 if "tiny" in model else 5
        self.initialized = True
        
        print(f"✅ Model loaded!")
        atexit.register(self.stop_server)
    
    def transcribe(self, audio_path: str) -> str:
        """Transcribe using the loaded model"""
        if not self.initialized:
            raise Exception("Model not loaded. Call start_server() first.")
        
        try:
            # Load audio
            sampled_audio = load_audio(audio_path)
            
            # Improve audio
            sampled_audio, start_time = improve_input_audio(sampled_audio, vad=True)
            chunk_offset = max(0, start_time - 0.2)
            
            # Preprocess
            mel_spectrograms = preprocess(
                sampled_audio,
                is_nhwc=True,
                chunk_length=self.chunk_length,
                chunk_offset=chunk_offset
            )
            
            # Transcribe
            for mel in mel_spectrograms:
                self._pipeline.send_data(mel)
                time.sleep(0.1)
            
            transcription = clean_transcription(self._pipeline.get_transcription())
            return transcription
            
        except Exception as e:
            print(f" Error: {e}")
            return None
    
    def stop_server(self):
        """Cleanup"""
        self.initialized = False
        print(" Model unloaded")


# Global instance
whisper_manager = WhisperManager()


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio"""
    return whisper_manager.transcribe(audio_path)
