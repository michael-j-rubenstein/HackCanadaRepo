import React, { useState } from "react";
import {
  Alert,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { colors } from "../theme/theme";

interface Props {
  onSubmit: (data: { price: number; store_name: string; date_observed: string }) => void;
  loading?: boolean;
}

const STORES = ["Loblaws", "Metro", "No Frills", "Walmart", "Costco"];

export default function PriceSubmitForm({ onSubmit, loading }: Props) {
  const [price, setPrice] = useState("");
  const [store, setStore] = useState(STORES[0]);
  const today = new Date().toISOString().slice(0, 10);
  const [dateStr, setDateStr] = useState(today);

  const handleSubmit = () => {
    const parsed = parseFloat(price);
    if (isNaN(parsed) || parsed <= 0) {
      Alert.alert("Invalid price", "Please enter a valid price.");
      return;
    }
    onSubmit({ price: parsed, store_name: store, date_observed: dateStr });
    setPrice("");
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Price ($)</Text>
      <TextInput
        style={styles.input}
        value={price}
        onChangeText={setPrice}
        placeholder="4.99"
        keyboardType="decimal-pad"
        placeholderTextColor={colors.textMuted}
      />

      <Text style={styles.label}>Store</Text>
      <View style={styles.storeRow}>
        {STORES.map((s) => (
          <TouchableOpacity
            key={s}
            style={[styles.storeChip, store === s && styles.storeChipActive]}
            onPress={() => setStore(s)}
          >
            <Text
              style={[styles.storeChipText, store === s && styles.storeChipTextActive]}
            >
              {s}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Date Observed</Text>
      <TextInput
        style={styles.input}
        value={dateStr}
        onChangeText={setDateStr}
        placeholder="YYYY-MM-DD"
        placeholderTextColor={colors.textMuted}
      />

      <TouchableOpacity
        style={[styles.submitBtn, loading && styles.submitBtnDisabled]}
        onPress={handleSubmit}
        disabled={loading}
      >
        <Text style={styles.submitText}>{loading ? "Submitting..." : "Submit Price"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  label: { fontSize: 14, fontWeight: "600", color: colors.textSecondary, marginBottom: 6, marginTop: 12 },
  input: {
    backgroundColor: colors.bgInput,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 16,
    color: colors.textPrimary,
  },
  storeRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  storeChip: {
    backgroundColor: colors.bgInput,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  storeChipActive: { backgroundColor: colors.accent, borderColor: colors.accent },
  storeChipText: { fontSize: 13, color: colors.textSecondary },
  storeChipTextActive: { color: colors.bgDeepest, fontWeight: "600" },
  submitBtn: {
    backgroundColor: colors.accent,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 20,
  },
  submitBtnDisabled: { opacity: 0.6 },
  submitText: { color: colors.bgDeepest, fontSize: 16, fontWeight: "700" },
});
