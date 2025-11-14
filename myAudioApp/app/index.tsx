import { View, Text, FlatList, StyleSheet, Pressable } from "react-native";
import { products } from "../constants/menu";
import MenuItemCard from "../components/MenuItemCard";
import { Link } from "expo-router";

export default function MenuScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.headerRow}>
        <Text style={styles.title}>Menu</Text>

        {/* Go to Voice Order screen */}
        <Link href="/order">
          <Text style={styles.orderBtn}>🎤 Voice Order</Text>
        </Link>
      </View>

      <FlatList
        data={products}
        numColumns={2}
        contentContainerStyle={{ gap: 14, paddingTop: 20 }}
        columnWrapperStyle={{ gap: 14 }}
        renderItem={({ item }) => <MenuItemCard item={item} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0b0d10",
    paddingHorizontal: 16,
    paddingTop: 40,
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  title: {
    color: "white",
    fontSize: 28,
    fontWeight: "700",
  },
  orderBtn: {
    color: "#4ade80",
    fontSize: 14,
    borderWidth: 1,
    borderColor: "#4ade80",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
});
