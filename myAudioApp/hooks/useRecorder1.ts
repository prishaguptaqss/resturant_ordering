import { useEffect, useRef, useState } from "react";
import { Platform, Alert } from "react-native";
import { Audio } from "expo-av";

const PI_SERVER = "http://192.168.1.213:8000/audio"; 

export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [uri, setUri] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);
  const [permissionGranted, setPermissionGranted] = useState(false);

  const recRef = useRef<Audio.Recording | null>(null);
  const timerRef = useRef<any>(null);

  useEffect(() => {
    const setupAudio = async () => {
      try {
        // Request permissions first
        const { status, canAskAgain, granted } = await Audio.requestPermissionsAsync();
        
        console.log('Permission status:', { status, canAskAgain, granted });
        
        if (status !== 'granted') {
          Alert.alert(
            'Permission Required',
            'Please grant microphone permission to record audio.',
            [{ text: 'OK' }]
          );
          setPermissionGranted(false);
          return;
        }
        
        setPermissionGranted(true);
        
        // Set audio mode after permissions are granted
        const mode: any = {
          staysActiveInBackground: true,
          shouldDuckAndroid: true,
          playThroughEarpieceAndroid: false,
        };
        
        if (Platform.OS === 'ios') {
          mode.allowsRecordingIOS = true;
          mode.playsInSilentModeIOS = true;
        }
        
        await Audio.setAudioModeAsync(mode);
        console.log('Audio mode set successfully');
        
      } catch (error) {
        console.error('Error setting up audio:', error);
        Alert.alert('Setup Error', 'Failed to set up audio recording.');
      }
    };
    
    setupAudio();
  }, []);

  const start = async () => {
    try {
      // Check permissions again before recording
      const { status } = await Audio.getPermissionsAsync();
      
      if (status !== 'granted') {
        const { status: newStatus } = await Audio.requestPermissionsAsync();
        if (newStatus !== 'granted') {
          Alert.alert(
            'Permission Denied',
            'Cannot record audio without microphone permission.'
          );
          return;
        }
      }
      
      const mode: any = {
        staysActiveInBackground: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      };
      
      if (Platform.OS === 'ios') {
        mode.allowsRecordingIOS = true;
        mode.playsInSilentModeIOS = true;
      }
      
      await Audio.setAudioModeAsync(mode);
      
      const r = new Audio.Recording();
      await r.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await r.startAsync();
      
      recRef.current = r;
      setRecording(true);
      setSeconds(0);

      timerRef.current = setInterval(() => {
        setSeconds((t) => t + 1);
      }, 1000);
      
      console.log('Recording started successfully');
      
    } catch (error) {
      const err = error as Error;
      console.error('Error starting recording:', error);
      Alert.alert('Recording Error', 'Failed to start recording: ' + (err.message || "Unknown error"));
    }
  };

  const stop = async () => {
    try {
      clearInterval(timerRef.current);
      const r = recRef.current;
      if (!r) return;

      await r.stopAndUnloadAsync();
      const fileUri = r.getURI();
      setUri(fileUri || null);

      setRecording(false);
      recRef.current = null;

      console.log('Recording stopped. File URI:', fileUri);

      if (fileUri) {
        const transcriptionText = await uploadAudio(fileUri);
        setTranscription(transcriptionText);
      }

      return fileUri;
    } catch (error) {
      console.error('Error stopping recording:', error);
    }
  };

  const toggle = async () => {
    if (recording) return stop();
    else return start();
  };

  const uploadAudio = async (fileUri: string) => {
    try {
      // Platform-specific MIME types
      const fileType = Platform.OS === 'ios' ? 'audio/m4a' : 'audio/mp4';
      const fileName = Platform.OS === 'ios' ? 'voice.m4a' : 'voice.mp4';
      
      const form = new FormData();
      form.append("file", {
        uri: fileUri,
        type: fileType,
        name: fileName,
      } as any);

      console.log('Uploading audio from:', fileUri);
      
      const response = await fetch(PI_SERVER, {
        method: "POST",
        body: form,
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Server response:', data);
      return data.transcription;
    } catch (error) {
      console.error('Upload error:', error);
      const err = error as Error;
      Alert.alert('Upload Error', 'Failed to upload audio: ' + (err.message || "Unknown error"));
      throw error;
    }
  };

  return { recording, seconds, uri, toggle, uploadAudio, transcription, permissionGranted };
}