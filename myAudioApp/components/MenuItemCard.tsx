import { View, Text, Image, StyleSheet, Pressable } from "react-native";
import { MenuItem } from "../constants/types";

type Props = {
  item: MenuItem;
};

export default function MenuItemCard({ item }: Props) {
  return (
    <View style={styles.card}>
      <Image source={{ uri: item.img }} style={styles.image} />

      <Text style={styles.name}>{item.name}</Text>
      {/* <Text style={styles.cat}>{item.cat}</Text> */}
      <Text style={styles.price}>₹{item.price}</Text>

      {/* <Pressable style={styles.addBtn}>
        <Text style={styles.addText}>Add</Text>
      </Pressable> */}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    backgroundColor: "#1a1d21",
    padding: 12,
    borderRadius: 14,
  },
  image: {
    width: "100%",
    height: 120,
    borderRadius: 12,
  },
  name: {
    color: "white",
    fontSize: 15,
    marginTop: 10,
    fontWeight: "600",
  },
  // cat: {
  //   color: "#aaa",
  //   fontSize: 12,
  // },
  price: {
    color: "white",
    marginTop: 4,
    fontWeight: "600",
  },
  addBtn: {
    marginTop: 10,
    backgroundColor: "#111",
    borderWidth: 1,
    borderColor: "#333",
    paddingVertical: 8,
    borderRadius: 10,
    alignItems: "center",
  },
  addText: {
    color: "white",
    fontSize: 13,
  },
});
