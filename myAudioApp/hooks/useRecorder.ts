import { useEffect, useRef, useState } from "react";
import { Audio } from "expo-av";

const PI_SERVER = "http://192.168.1.213:8000/audio"; 

export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [uri, setUri] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);

  const recRef = useRef<Audio.Recording | null>(null);
  const timerRef = useRef<any>(null);

  useEffect(() => {
    const setAudioMode = async () => {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      await Audio.requestPermissionsAsync();
    };
    setAudioMode();
  }, []);

  const start = async () => {
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
    });
    const r = new Audio.Recording();
    await r.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
    await r.startAsync();
    recRef.current = r;
    setRecording(true);
    setSeconds(0);

    timerRef.current = setInterval(() => {
      setSeconds((t) => t + 1);
    }, 1000);
  };

  const stop = async () => {
    clearInterval(timerRef.current);
    const r = recRef.current;
    if (!r) return;

    await r.stopAndUnloadAsync();
    const fileUri = r.getURI();
    setUri(fileUri || null);

    setRecording(false);
    recRef.current = null;

    if (fileUri) {
      const transcriptionText = await uploadAudio(fileUri);
      setTranscription(transcriptionText);
    }

    return fileUri;
  };

  const toggle = async () => {
    if (recording) return stop();
    else return start();
  };

  const uploadAudio = async (fileUri: string) => {
    const form = new FormData();
    form.append("file", {
      uri: fileUri,
      type: "audio/m4a",
      name: "voice.m4a",
    } as any);

    const response = await fetch(PI_SERVER, {
      method: "POST",
      body: form,
      headers: { "Content-Type": "multipart/form-data" },
    });
    const data = await response.json();
    console.log(data)
    return data.transcription;
  };

  return { recording, seconds, uri, toggle, uploadAudio, transcription };
}
