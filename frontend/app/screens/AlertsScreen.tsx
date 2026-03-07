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
import AlertItem from "../components/AlertItem";
import {
  useGetAlertsQuery,
  useCreateAlertMutation,
  useDeleteAlertMutation,
  useGetItemsQuery,
} from "../../redux/api";

export default function AlertsScreen() {
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
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1d4ed8" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
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
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.pickerItem,
                    selectedItemId === item.id && styles.pickerItemActive,
                  ]}
                  onPress={() => setSelectedItemId(item.id)}
                >
                  <Text
                    style={[
                      styles.pickerText,
                      selectedItemId === item.id && styles.pickerTextActive,
                    ]}
                  >
                    {item.name} — ${item.current_price?.toFixed(2) ?? "?"}
                  </Text>
                </TouchableOpacity>
              )}
            />

            <Text style={styles.label}>Target Price ($)</Text>
            <TextInput
              style={styles.input}
              value={targetPrice}
              onChangeText={setTargetPrice}
              placeholder="3.99"
              keyboardType="decimal-pad"
              placeholderTextColor="#9ca3af"
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
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { flex: 1, backgroundColor: "#f9fafb" },
  list: { paddingVertical: 8 },
  empty: { textAlign: "center", color: "#9ca3af", marginTop: 40, fontSize: 15 },
  fab: {
    position: "absolute",
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#1d4ed8",
    justifyContent: "center",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  fabText: { color: "#fff", fontSize: 28, fontWeight: "600", marginTop: -2 },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "flex-end",
  },
  modal: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: "80%",
  },
  modalTitle: { fontSize: 20, fontWeight: "700", color: "#111", marginBottom: 16 },
  label: { fontSize: 14, fontWeight: "600", color: "#374151", marginBottom: 6, marginTop: 12 },
  itemPicker: { maxHeight: 200 },
  pickerItem: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 4,
    backgroundColor: "#f3f4f6",
  },
  pickerItemActive: { backgroundColor: "#1d4ed8" },
  pickerText: { fontSize: 14, color: "#374151" },
  pickerTextActive: { color: "#fff", fontWeight: "600" },
  input: {
    backgroundColor: "#f3f4f6",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 16,
    color: "#111",
  },
  modalButtons: { flexDirection: "row", justifyContent: "flex-end", gap: 12, marginTop: 20 },
  cancelBtn: { paddingVertical: 10, paddingHorizontal: 16 },
  cancelText: { color: "#6b7280", fontSize: 15, fontWeight: "600" },
  createBtn: {
    backgroundColor: "#1d4ed8",
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  createText: { color: "#fff", fontSize: 15, fontWeight: "700" },
});
