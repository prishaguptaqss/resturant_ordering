"""

Helper functions for audio processing and validation
"""
import os
import uuid
import wave
import struct
from fastapi import UploadFile
from pydub import AudioSegment

async def process_audio(file: UploadFile) -> str:
    """
    Convert uploaded audio to WAV format
    
    Args:
        file: Uploaded audio file (m4a, mp3, mp4, etc.)
    
    Returns:
        Path to converted WAV file
    """
    # Generate unique filename
    file_id = str(uuid.uuid4())
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save uploaded file
    input_path = os.path.join(upload_dir, f"{file_id}{os.path.splitext(file.filename)[1]}")
    
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Convert to WAV
    wav_path = os.path.join(upload_dir, f"{file_id}.wav")
    
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_frame_rate(16000)  # 16kHz
        audio.export(wav_path, format="wav")
        print(f"converted {input_path} to .wav")
    except Exception as e:
        print(f"Error converting audio: {e}")
        raise
    finally:
        # Clean up original file
        if os.path.exists(input_path):
            os.remove(input_path)
    
    return wav_path


def validate_audio(wav_path: str, min_duration: float = 0.5, min_amplitude: int = 500) -> tuple:
    """
    Validate audio file before processing
    
    Args:
        wav_path: Path to WAV file
        min_duration: Minimum duration in seconds (default: 0.5s)
        min_amplitude: Minimum audio amplitude (default: 500)
    
    Returns:
        Tuple of (is_valid, error_message, audio_info)
        audio_info contains: duration, max_level, sample_rate
    """
    try:
        with wave.open(wav_path, 'rb') as wav:
            # Get audio parameters
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            n_frames = wav.getnframes()
            
            # Calculate duration
            duration = n_frames / float(frame_rate)
            
            # Read audio data
            audio_data = wav.readframes(n_frames)
            
            # Calculate max amplitude
            # Unpack audio data as signed integers
            if sample_width == 1:  # 8-bit
                samples = struct.unpack(f"{n_frames * n_channels}b", audio_data)
            elif sample_width == 2:  # 16-bit (most common)
                samples = struct.unpack(f"{n_frames * n_channels}h", audio_data)
            elif sample_width == 4:  # 32-bit
                samples = struct.unpack(f"{n_frames * n_channels}i", audio_data)
            else:
                return False, f"Unsupported sample width: {sample_width}", {}
            
            # Get max amplitude (absolute value)
            max_amplitude = max(abs(s) for s in samples)
            
            # Normalize max_amplitude to 0-1 range for 16-bit audio
            if sample_width == 2:
                max_level = max_amplitude / 32768.0  # 16-bit max value
            else:
                max_level = max_amplitude / (2 ** (8 * sample_width - 1))
            
            audio_info = {
                "duration": round(duration, 2),
                "max_level": round(max_level, 3),
                "sample_rate": frame_rate,
                "channels": n_channels,
                "sample_width": sample_width
            }
            
            # Validation checks
            if duration < min_duration:
                return False, f"Audio too short: {duration:.2f}s (minimum {min_duration}s)", audio_info
            
            if max_amplitude < min_amplitude:
                return False, f"Audio too quiet: max_amplitude={max_amplitude} (minimum {min_amplitude}). Please speak louder.", audio_info
            
            return True, "", audio_info
            
    except Exception as e:
        return False, f"Audio validation error: {str(e)}", {}


def cleanup_old_files(directory: str = "uploads", max_age_minutes: int = 60):
    """
    Clean up old audio files (optional utility)
    
    Args:
        directory: Directory to clean
        max_age_minutes: Delete files older than this many minutes
    """
    import time
    
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_minutes * 60
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    print(f"🗑️  Cleaned up old file: {filename}")
                except Exception as e:
                    print(f"Error cleaning up {filename}: {e}")
