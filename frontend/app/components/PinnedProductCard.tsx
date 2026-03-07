import React from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { LineChart } from "react-native-gifted-charts";
import type { PinnedItem, PricePoint } from "../types/models";
import { colors } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

interface Props {
  item: PinnedItem;
  priceHistory: PricePoint[];
  onPress: (itemId: number, itemName: string) => void;
}

export default function PinnedProductCard({ item, priceHistory, onPress }: Props) {
  const change = item.price_change_pct ?? 0;
  const isUp = change > 0;
  const isDown = change < 0;
  const pillBg = isDown ? colors.positiveBg : isUp ? colors.negativeBg : colors.bgInput;
  const pillColor = isDown ? colors.positive : isUp ? colors.negative : colors.textMuted;
  const arrow = isDown ? "\u25BC" : isUp ? "\u25B2" : "";
  const emoji = getItemEmoji(item.item_name ?? "");

  const trendDown =
    priceHistory.length >= 2 &&
    priceHistory[priceHistory.length - 1].avg_price < priceHistory[0].avg_price;
  const lineColor = trendDown ? colors.positive : colors.negative;

  const chartData = priceHistory.map((p) => ({ value: p.avg_price }));

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={() => onPress(item.item_id, item.item_name ?? "Item")}
      activeOpacity={0.7}
    >
      <View style={styles.left}>
        <Text style={styles.emoji}>{emoji}</Text>
        <Text style={styles.name} numberOfLines={2}>
          {item.item_name ?? "Unknown"}
        </Text>
      </View>
      <View style={styles.middle}>
        <View style={styles.chartWrapper}>
          {chartData.length >= 2 ? (
            <LineChart
              data={chartData}
              height={50}
              width={100}
              color={lineColor}
              thickness={2}
              hideAxesAndRules
              hideDataPoints
              hideYAxisText
              hideOrigin
              curved
              curveType={0}
              areaChart
              startFillColor={lineColor}
              endFillColor="transparent"
              startOpacity={0.2}
              endOpacity={0}
              spacing={Math.floor(100 / Math.max(chartData.length - 1, 1))}
              initialSpacing={0}
              endSpacing={0}
              adjustToWidth
              disableScroll
              yAxisOffset={Math.min(...chartData.map((d) => d.value)) * 0.98}
            />
          ) : (
            <Text style={styles.noData}>No data</Text>
          )}
        </View>
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
    paddingHorizontal: 16,
    paddingVertical: 24,
    marginHorizontal: 16,
    marginVertical: 5,
    minHeight: 115,
  },
  left: { flex: 0.8, alignItems: "flex-start" },
  emoji: { fontSize: 32, marginBottom: 4 },
  name: { fontSize: 14, fontWeight: "600", color: colors.textPrimary },
  middle: { flex: 1.4, alignItems: "center", justifyContent: "center", marginHorizontal: 4 },
  chartWrapper: {
    width: 100,
    height: 50,
    overflow: "hidden",
    alignItems: "center",
    justifyContent: "center",
  },
  price: { fontSize: 18, fontWeight: "700", color: colors.textPrimary, marginBottom: 4 },
  pill: {
    borderRadius: 99,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  pillText: { fontSize: 12, fontWeight: "600" },
  right: { width: 90, alignItems: "flex-end", justifyContent: "center" },
  noData: { fontSize: 12, color: colors.textMuted },
});
