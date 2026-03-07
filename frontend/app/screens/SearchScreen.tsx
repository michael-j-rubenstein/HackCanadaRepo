import React, { useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import SearchBar from "../components/SearchBar";
import GroceryItemCard from "../components/GroceryItemCard";
import { useGetItemsQuery } from "../../redux/api";
import type { GroceryItem } from "../types/models";
import type { HomeStackParamList } from "../routing/types";

type Nav = NativeStackNavigationProp<HomeStackParamList, "HomeList">;

export default function SearchScreen() {
  const [query, setQuery] = useState("");
  const { data: items, isLoading } = useGetItemsQuery(
    query ? { search: query } : undefined
  );
  const navigation = useNavigation<Nav>();

  const handlePress = (item: GroceryItem) => {
    navigation.navigate("ProductDetail", { itemId: item.id, itemName: item.name });
  };

  return (
    <View style={styles.container}>
      <SearchBar onSearch={setQuery} />
      {isLoading ? (
        <ActivityIndicator style={{ marginTop: 20 }} size="large" color="#1d4ed8" />
      ) : (
        <FlatList
          data={items ?? []}
          keyExtractor={(item) => String(item.id)}
          renderItem={({ item }) => (
            <GroceryItemCard item={item} onPress={handlePress} />
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>
              {query ? "No items found" : "Search for grocery items"}
            </Text>
          }
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f9fafb" },
  list: { paddingBottom: 20 },
  empty: { textAlign: "center", color: "#9ca3af", marginTop: 40, fontSize: 15 },
});
