import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { LineChart } from "react-native-gifted-charts";
import type { PricePoint } from "../types/models";
import { colors } from "../theme/theme";

interface Props {
  data: PricePoint[];
}

export default function PriceChart({ data }: Props) {
  if (!data || data.length === 0) {
    return (
      <View style={styles.empty}>
        <Text style={styles.emptyText}>No price history available</Text>
      </View>
    );
  }

  const chartData = data.map((p) => ({
    value: p.avg_price,
    label: p.date.slice(5),
  }));

  const prices = data.map((p) => p.avg_price);
  const minPrice = Math.min(...prices);
  const yMin = Math.floor(minPrice * 0.95 * 100) / 100;

  const isDown = data.length >= 2 && data[data.length - 1].avg_price < data[0].avg_price;
  const lineColor = isDown ? colors.positive : colors.negative;

  return (
    <View style={styles.container}>
      <LineChart
        data={chartData}
        height={180}
        width={300}
        color={lineColor}
        thickness={2}
        dataPointsColor={lineColor}
        dataPointsRadius={3}
        yAxisTextStyle={styles.axisText}
        xAxisLabelTextStyle={[styles.axisText, { width: 40 }]}
        noOfSections={4}
        yAxisOffset={yMin}
        spacing={chartData.length > 15 ? 20 : 40}
        hideRules
        curved
        startFillColor={lineColor}
        endFillColor="transparent"
        startOpacity={0.15}
        endOpacity={0}
        areaChart
        showVerticalLines={false}
        xAxisLabelsVerticalShift={2}
        yAxisColor={colors.border}
        xAxisColor={colors.border}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginHorizontal: 16,
  },
  axisText: { fontSize: 10, color: colors.textMuted },
  empty: { padding: 40, alignItems: "center" },
  emptyText: { color: colors.textSecondary, fontSize: 14 },
});
