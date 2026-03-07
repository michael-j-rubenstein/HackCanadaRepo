import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import PriceSubmitForm from "../components/PriceSubmitForm";
import { useGetItemsQuery, useSubmitPriceMutation } from "../../redux/api";

export default function SubmitPriceScreen() {
  const { data: items, isLoading } = useGetItemsQuery();
  const [submitPrice, { isLoading: submitting }] = useSubmitPriceMutation();
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);

  const selectedItem = items?.find((i) => i.id === selectedItemId);

  const handleSubmit = async (data: { price: number; store_name: string; date_observed: string }) => {
    if (!selectedItemId) {
      Alert.alert("Select an item first");
      return;
    }
    try {
      await submitPrice({ itemId: selectedItemId, body: data }).unwrap();
      Alert.alert("Success", "Price submitted!");
    } catch {
      Alert.alert("Error", "Failed to submit price.");
    }
  };

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1d4ed8" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Select an Item</Text>
      <FlatList
        data={items ?? []}
        keyExtractor={(i) => String(i.id)}
        scrollEnabled={false}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[styles.itemRow, selectedItemId === item.id && styles.itemRowActive]}
            onPress={() => setSelectedItemId(item.id)}
          >
            <Text style={[styles.itemText, selectedItemId === item.id && styles.itemTextActive]}>
              {item.name}
            </Text>
            <Text style={[styles.itemPrice, selectedItemId === item.id && styles.itemTextActive]}>
              ${item.current_price?.toFixed(2) ?? "—"}
            </Text>
          </TouchableOpacity>
        )}
      />

      {selectedItem && (
        <>
          <Text style={styles.subtitle}>
            Submitting price for: {selectedItem.name}
          </Text>
          <PriceSubmitForm onSubmit={handleSubmit} loading={submitting} />
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { flex: 1, backgroundColor: "#f9fafb" },
  content: { paddingBottom: 40 },
  title: {
    fontSize: 20,
    fontWeight: "700",
    color: "#111",
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1d4ed8",
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  itemRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginVertical: 2,
    borderRadius: 8,
    backgroundColor: "#fff",
  },
  itemRowActive: { backgroundColor: "#1d4ed8" },
  itemText: { fontSize: 15, color: "#111" },
  itemPrice: { fontSize: 15, color: "#6b7280" },
  itemTextActive: { color: "#fff", fontWeight: "600" },
});
