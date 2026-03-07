import React from "react";
import { FlatList, StyleSheet, Text, View } from "react-native";
import GroceryItemCard from "./GroceryItemCard";
import type { GroceryItem } from "../types/models";

interface Props {
  title: string;
  items: GroceryItem[];
  onItemPress: (item: GroceryItem) => void;
}

export default function CategorySection({ title, items, onItemPress }: Props) {
  return (
    <View style={styles.section}>
      <Text style={styles.header}>{title}</Text>
      <FlatList
        data={items}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <GroceryItemCard item={item} onPress={onItemPress} />
        )}
        scrollEnabled={false}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  section: { marginBottom: 16 },
  header: {
    fontSize: 20,
    fontWeight: "700",
    color: "#111",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
});
