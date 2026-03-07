import React from "react";
import { Dimensions, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import type { GroceryItem } from "../types/models";
import { colors } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

const SCREEN_WIDTH = Dimensions.get("window").width;
export const CARD_WIDTH = (SCREEN_WIDTH - 48) / 2;

interface Props {
  item: GroceryItem;
  onPress: (item: GroceryItem) => void;
}

export default function GrocerySquareCard({ item, onPress }: Props) {
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
      <Text style={styles.name} numberOfLines={2}>{item.name}</Text>
      <Text style={styles.price}>
        ${item.current_price?.toFixed(2) ?? "\u2014"}
      </Text>
      <View style={[styles.pill, { backgroundColor: pillBg }]}>
        <Text style={[styles.pillText, { color: pillColor }]}>
          {arrow} {Math.abs(change).toFixed(1)}%
        </Text>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    width: CARD_WIDTH,
    backgroundColor: colors.bgCard,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  emoji: { fontSize: 40, marginBottom: 8 },
  name: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.textPrimary,
    textAlign: "center",
    marginBottom: 6,
  },
  price: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: 6,
  },
  pill: {
    borderRadius: 99,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  pillText: { fontSize: 12, fontWeight: "600" },
});
