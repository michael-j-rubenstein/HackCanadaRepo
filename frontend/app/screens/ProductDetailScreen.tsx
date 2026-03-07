import React from "react";
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import PriceChart from "../components/PriceChart";
import PriceSubmitForm from "../components/PriceSubmitForm";
import {
  useGetItemQuery,
  useGetPriceHistoryQuery,
  useSubmitPriceMutation,
} from "../../redux/api";
import type { HomeStackParamList } from "../routing/types";
import { colors, gradients } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

type Props = NativeStackScreenProps<HomeStackParamList, "ProductDetail">;

export default function ProductDetailScreen({ route }: Props) {
  const { itemId } = route.params;
  const { data: item, isLoading: itemLoading } = useGetItemQuery(itemId);
  const { data: history, isLoading: historyLoading } = useGetPriceHistoryQuery({ id: itemId });
  const [submitPrice, { isLoading: submitting }] = useSubmitPriceMutation();

  const handleSubmit = async (data: { price: number; store_name: string; date_observed: string }) => {
    try {
      await submitPrice({ itemId, body: data }).unwrap();
      Alert.alert("Success", "Price submitted!");
    } catch {
      Alert.alert("Error", "Failed to submit price.");
    }
  };

  if (itemLoading) {
    return (
      <LinearGradient colors={gradients.main} style={styles.center}>
        <ActivityIndicator size="large" color={colors.accent} />
      </LinearGradient>
    );
  }

  if (!item) {
    return (
      <View style={[styles.center, { backgroundColor: colors.bgDeepest }]}>
        <Text style={{ color: colors.textSecondary }}>Item not found</Text>
      </View>
    );
  }

  const change = item.price_change_pct ?? 0;
  const isUp = change > 0;
  const isDown = change < 0;
  const pillBg = isDown ? colors.positiveBg : isUp ? colors.negativeBg : colors.bgInput;
  const pillColor = isDown ? colors.positive : isUp ? colors.negative : colors.textMuted;
  const emoji = getItemEmoji(item.name, item.category_name);

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <LinearGradient colors={gradients.main} style={styles.header}>
        <Text style={styles.emoji}>{emoji}</Text>
        <Text style={styles.name}>{item.name}</Text>
        {item.brand && <Text style={styles.brand}>{item.brand} - {item.unit}</Text>}
        <View style={styles.priceRow}>
          <Text style={styles.price}>${item.current_price?.toFixed(2) ?? "\u2014"}</Text>
          <View style={[styles.pill, { backgroundColor: pillBg }]}>
            <Text style={[styles.pillText, { color: pillColor }]}>
              {isUp ? "+" : ""}{change.toFixed(1)}%
            </Text>
          </View>
        </View>
      </LinearGradient>

      <Text style={styles.sectionTitle}>30-Day Price History</Text>
      {historyLoading ? (
        <ActivityIndicator style={{ marginVertical: 20 }} color={colors.accent} />
      ) : (
        <PriceChart data={history ?? []} />
      )}

      <Text style={styles.sectionTitle}>Submit a Price</Text>
      <PriceSubmitForm onSubmit={handleSubmit} loading={submitting} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  scroll: { flex: 1, backgroundColor: colors.bgDeepest },
  content: { paddingBottom: 40 },
  header: {
    padding: 20,
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  emoji: { fontSize: 48, marginBottom: 8 },
  name: { fontSize: 24, fontWeight: "700", color: colors.textPrimary },
  brand: { fontSize: 15, color: colors.textMuted, marginTop: 4 },
  priceRow: { flexDirection: "row", alignItems: "center", marginTop: 8, gap: 10 },
  price: { fontSize: 28, fontWeight: "700", color: colors.textPrimary },
  pill: {
    borderRadius: 99,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  pillText: { fontSize: 14, fontWeight: "600" },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textPrimary,
    paddingHorizontal: 16,
    paddingTop: 20,
    paddingBottom: 10,
  },
});
