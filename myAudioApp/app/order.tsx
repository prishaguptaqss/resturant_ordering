import { View, Text, StyleSheet, Alert } from "react-native";
import { useEffect } from "react";
import { MicButton } from "../components/MicButton";
import { useRecorder } from "../hooks/useRecorder";
import { Link } from "expo-router";

export default function OrderScreen() {
  const { recording, seconds, uri, toggle, uploadAudio, transcription } = useRecorder();

  useEffect(() => {
    if (transcription) {
      Alert.alert("Transcription", transcription, [{ text: "OK" }]);
    }
  }, [transcription]);

  return (
    <View style={styles.container}>
      <Link href="/">
        <Text style={styles.backBtn}>← Menu</Text>
      </Link>

      <Text style={styles.title}>Voice Order</Text>

      <MicButton recording={recording} onToggle={toggle} />

      <Text style={styles.timer}>
        {String(Math.floor(seconds / 60)).padStart(2, "0")}:
        {String(seconds % 60).padStart(2, "0")}
      </Text>

      <Text style={styles.hint}>
        {recording ? "Recording…" : "Tap mic to start order"}
      </Text>

      {/* {uri ? <Text style={styles.saved}>Saved: {uri}</Text> : null} */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b0d10",
    padding: 20,
    paddingTop: 60,
  },
  backBtn: { color: "#4ade80", fontSize: 14, marginBottom: 20 },
  title: { color: "white", fontSize: 30, fontWeight: "700", marginBottom: 40 },
  timer: {
    color: "white",
    fontSize: 40,
    marginTop: 30,
    textAlign: "center",
  },
  hint: { color: "#aaa", textAlign: "center", marginTop: 10 },
  saved: { marginTop: 10, color: "#999", fontSize: 12, textAlign: "center" },
});

