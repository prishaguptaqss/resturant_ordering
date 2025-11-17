import { Pressable, StyleSheet, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";

interface MicButtonProps {
  recording: boolean;
  onToggle: () => void;
  disabled?: boolean;
}

export function MicButton({ recording, onToggle, disabled = false }: MicButtonProps) {
  return (
    <View style={styles.container}>
      <Pressable
        onPress={onToggle}
        disabled={disabled}
        style={({ pressed }) => [
          styles.button,
          recording && styles.recording,
          disabled && styles.disabled,
          pressed && !disabled && styles.pressed,
        ]}
      >
        <Ionicons
          name={recording ? "stop" : "mic"}
          size={48}
          color={disabled ? "#666" : "white"}
        />
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 20,
  },
  button: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "#4ade80",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#4ade80",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  recording: {
    backgroundColor: "#ef4444",
    shadowColor: "#ef4444",
  },
  disabled: {
    backgroundColor: "#333",
    shadowOpacity: 0.2,
    shadowColor: "#666",
  },
  pressed: {
    transform: [{ scale: 0.95 }],
    opacity: 0.8,
  },
});