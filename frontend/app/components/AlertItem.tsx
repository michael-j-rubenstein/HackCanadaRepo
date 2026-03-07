import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import type { PriceAlert } from "../types/models";
import { colors } from "../theme/theme";

interface Props {
  alert: PriceAlert;
  onDelete: (id: number) => void;
}

export default function AlertItem({ alert, onDelete }: Props) {
  return (
    <View style={[styles.card, alert.is_triggered && styles.triggered]}>
      <View style={styles.left}>
        <Text style={styles.name}>{alert.item_name ?? `Item #${alert.item_id}`}</Text>
        <Text style={styles.target}>Target: ${alert.target_price.toFixed(2)}</Text>
        {alert.is_triggered && (
          <Text style={styles.triggeredText}>Triggered!</Text>
        )}
      </View>
      <TouchableOpacity style={styles.deleteBtn} onPress={() => onDelete(alert.id)}>
        <Text style={styles.deleteText}>Remove</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 14,
    marginHorizontal: 16,
    marginVertical: 4,
  },
  triggered: { borderLeftWidth: 3, borderLeftColor: colors.positive },
  left: { flex: 1 },
  name: { fontSize: 16, fontWeight: "600", color: colors.textPrimary },
  target: { fontSize: 13, color: colors.textSecondary, marginTop: 2 },
  triggeredText: { fontSize: 13, color: colors.positive, fontWeight: "600", marginTop: 2 },
  deleteBtn: {
    backgroundColor: colors.negativeBg,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  deleteText: { color: colors.negative, fontSize: 13, fontWeight: "600" },
});
