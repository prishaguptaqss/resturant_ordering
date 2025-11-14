import { Pressable, StyleSheet } from "react-native";
import { Mic } from "lucide-react-native";

type MicButtonProps = {
  recording: boolean;
  onToggle: () => void;
};

export function MicButton({ recording, onToggle }: MicButtonProps) {
  return (
    <Pressable
      onPress={onToggle}
      style={[
        styles.btn,
        { backgroundColor: recording ? "#ef4444" : "white" }
      ]}
    >
      <Mic size={46} color={recording ? "white" : "black"} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    height: 140,
    width: 140,
    borderRadius: 100,
    justifyContent: "center",
    alignItems: "center",
    alignSelf: "center",
    elevation: 8,
  },
});
