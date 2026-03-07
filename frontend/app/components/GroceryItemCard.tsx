import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import type { GroceryItem } from "../types/models";
import { colors } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

interface Props {
  item: GroceryItem;
  onPress: (item: GroceryItem) => void;
}

export default function GroceryItemCard({ item, onPress }: Props) {
  const change = item.price_change_pct ?? 0;
  const isUp = change > 0;
  const isDown = change < 0;
  const pillBg = isDown ? colors.positiveBg : isUp ? colors.negativeBg : colors.bgInput;
  const pillColor = isDown ? colors.positive : isUp ? colors.negative : colors.textMuted;
  const arrow = isDown ? "\u25BC" : isUp ? "\u25B2" : "";
  const emoji = getItemEmoji(item.name, item.category_name);

  return (
    <TouchableOpacity style={styles.card} onPress={() => onPress(item)} activeOpacity={0.7}>
      <Text style={styles.emoji}>{emoji}</Text>
      <View style={styles.mid}>
        <Text style={styles.name} numberOfLines={1}>{item.name}</Text>
        <Text style={styles.sub}>
          {item.brand ? `${item.brand} \u00B7 ` : ""}{item.unit}
        </Text>
      </View>
      <View style={styles.right}>
        <Text style={styles.price}>
          ${item.current_price?.toFixed(2) ?? "\u2014"}
        </Text>
        <View style={[styles.pill, { backgroundColor: pillBg }]}>
          <Text style={[styles.pillText, { color: pillColor }]}>
            {arrow} {Math.abs(change).toFixed(1)}%
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 14,
    marginHorizontal: 16,
    marginVertical: 4,
  },
  emoji: { fontSize: 32, marginRight: 12 },
  mid: { flex: 1, marginRight: 12 },
  name: { fontSize: 16, fontWeight: "600", color: colors.textPrimary },
  sub: { fontSize: 13, color: colors.textMuted, marginTop: 2 },
  right: { alignItems: "flex-end" },
  price: { fontSize: 18, fontWeight: "700", color: colors.textPrimary },
  pill: {
    borderRadius: 99,
    paddingHorizontal: 10,
    paddingVertical: 3,
    marginTop: 4,
  },
  pillText: { fontSize: 12, fontWeight: "600" },
});
