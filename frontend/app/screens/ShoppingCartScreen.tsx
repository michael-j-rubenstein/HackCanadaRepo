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
import { LinearGradient } from "expo-linear-gradient";
import PriceSubmitForm from "../components/PriceSubmitForm";
import { useGetItemsQuery, useSubmitPriceMutation } from "../../redux/api";
import { colors, gradients } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

export default function ShoppingCartScreen() {
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
      <LinearGradient colors={gradients.main} style={styles.center}>
        <ActivityIndicator size="large" color={colors.accent} />
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={gradients.main} style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Select an Item</Text>
        <FlatList
          data={items ?? []}
          keyExtractor={(i) => String(i.id)}
          scrollEnabled={false}
          renderItem={({ item }) => {
            const active = selectedItemId === item.id;
            return (
              <TouchableOpacity
                style={[styles.itemRow, active && styles.itemRowActive]}
                onPress={() => setSelectedItemId(item.id)}
              >
                <Text style={styles.itemEmoji}>
                  {getItemEmoji(item.name, item.category_name)}
                </Text>
                <Text style={[styles.itemText, active && styles.itemTextActive]}>
                  {item.name}
                </Text>
                <Text style={[styles.itemPrice, active && styles.itemTextActive]}>
                  ${item.current_price?.toFixed(2) ?? "\u2014"}
                </Text>
              </TouchableOpacity>
            );
          }}
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
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  content: { paddingBottom: 40 },
  title: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.textPrimary,
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.accent,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  itemRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginVertical: 2,
    borderRadius: 8,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
  },
  itemRowActive: { backgroundColor: colors.accent, borderColor: colors.accent },
  itemEmoji: { fontSize: 20, marginRight: 10 },
  itemText: { fontSize: 15, color: colors.textPrimary, flex: 1 },
  itemPrice: { fontSize: 15, color: colors.textSecondary },
  itemTextActive: { color: colors.bgDeepest, fontWeight: "600" },
});
