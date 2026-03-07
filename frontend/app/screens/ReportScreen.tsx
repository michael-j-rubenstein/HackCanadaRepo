import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Modal,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import AlertItem from "../components/AlertItem";
import {
  useGetAlertsQuery,
  useCreateAlertMutation,
  useDeleteAlertMutation,
  useGetItemsQuery,
} from "../../redux/api";
import { colors, gradients } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

export default function ReportScreen() {
  const { data: alerts, isLoading } = useGetAlertsQuery();
  const { data: items } = useGetItemsQuery();
  const [createAlert] = useCreateAlertMutation();
  const [deleteAlert] = useDeleteAlertMutation();

  const [modalVisible, setModalVisible] = useState(false);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [targetPrice, setTargetPrice] = useState("");

  const handleDelete = async (id: number) => {
    try {
      await deleteAlert(id).unwrap();
    } catch {
      Alert.alert("Error", "Failed to delete alert.");
    }
  };

  const handleCreate = async () => {
    if (!selectedItemId) {
      Alert.alert("Select an item");
      return;
    }
    const price = parseFloat(targetPrice);
    if (isNaN(price) || price <= 0) {
      Alert.alert("Enter a valid price");
      return;
    }
    try {
      await createAlert({ item_id: selectedItemId, target_price: price }).unwrap();
      setModalVisible(false);
      setTargetPrice("");
      setSelectedItemId(null);
    } catch {
      Alert.alert("Error", "Failed to create alert.");
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
      <FlatList
        data={alerts ?? []}
        keyExtractor={(a) => String(a.id)}
        renderItem={({ item }) => (
          <AlertItem alert={item} onDelete={handleDelete} />
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>No alerts yet. Tap + to create one.</Text>
        }
        contentContainerStyle={styles.list}
      />

      <TouchableOpacity style={styles.fab} onPress={() => setModalVisible(true)}>
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>

      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <Text style={styles.modalTitle}>Create Price Alert</Text>

            <Text style={styles.label}>Select Item</Text>
            <FlatList
              data={items ?? []}
              keyExtractor={(i) => String(i.id)}
              style={styles.itemPicker}
              renderItem={({ item }) => {
                const active = selectedItemId === item.id;
                return (
                  <TouchableOpacity
                    style={[styles.pickerItem, active && styles.pickerItemActive]}
                    onPress={() => setSelectedItemId(item.id)}
                  >
                    <Text style={[styles.pickerText, active && styles.pickerTextActive]}>
                      {getItemEmoji(item.name, item.category_name)} {item.name} — ${item.current_price?.toFixed(2) ?? "?"}
                    </Text>
                  </TouchableOpacity>
                );
              }}
            />

            <Text style={styles.label}>Target Price ($)</Text>
            <TextInput
              style={styles.input}
              value={targetPrice}
              onChangeText={setTargetPrice}
              placeholder="3.99"
              keyboardType="decimal-pad"
              placeholderTextColor={colors.textMuted}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.createBtn} onPress={handleCreate}>
                <Text style={styles.createText}>Create</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  list: { paddingVertical: 8 },
  empty: { textAlign: "center", color: colors.textSecondary, marginTop: 40, fontSize: 15 },
  fab: {
    position: "absolute",
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.accent,
    justifyContent: "center",
    alignItems: "center",
  },
  fabText: { color: colors.bgDeepest, fontSize: 28, fontWeight: "600", marginTop: -2 },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.6)",
    justifyContent: "flex-end",
  },
  modal: {
    backgroundColor: colors.bgSection,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: "80%",
  },
  modalTitle: { fontSize: 20, fontWeight: "700", color: colors.textPrimary, marginBottom: 16 },
  label: { fontSize: 14, fontWeight: "600", color: colors.textSecondary, marginBottom: 6, marginTop: 12 },
  itemPicker: { maxHeight: 200 },
  pickerItem: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 4,
    backgroundColor: colors.bgInput,
  },
  pickerItemActive: { backgroundColor: colors.accent },
  pickerText: { fontSize: 14, color: colors.textPrimary },
  pickerTextActive: { color: colors.bgDeepest, fontWeight: "600" },
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
  modalButtons: { flexDirection: "row", justifyContent: "flex-end", gap: 12, marginTop: 20 },
  cancelBtn: { paddingVertical: 10, paddingHorizontal: 16 },
  cancelText: { color: colors.textMuted, fontSize: 15, fontWeight: "600" },
  createBtn: {
    backgroundColor: colors.accent,
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  createText: { color: colors.bgDeepest, fontSize: 15, fontWeight: "700" },
});
