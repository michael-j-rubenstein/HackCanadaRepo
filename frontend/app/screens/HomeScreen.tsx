import React, { useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import Svg, { Circle } from "react-native-svg";
import { useGetPinsQuery, useGetPriceHistoryQuery } from "../../redux/api";
import PinnedProductCard from "../components/PinnedProductCard";
import type { PinnedItem } from "../types/models";
import type { HomeStackParamList } from "../routing/types";
import { colors, gradients } from "../theme/theme";

type Nav = NativeStackNavigationProp<HomeStackParamList, "HomeDashboard">;

function calculateSavings(pins: PinnedItem[]) {
  if (!pins?.length) return { percentile: 50, totalSaved: 0 };
  const drops = pins.filter((p) => (p.price_change_pct ?? 0) < 0);
  const avgDropPct =
    drops.length > 0
      ? drops.reduce((s, p) => s + Math.abs(p.price_change_pct ?? 0), 0) / pins.length
      : 0;
  const totalSaved = drops.reduce((s, p) => {
    return s + ((p.current_price ?? 0) * Math.abs(p.price_change_pct ?? 0)) / 100;
  }, 0);
  const percentile = Math.max(1, Math.round(50 - avgDropPct * 5 - pins.length));
  return { percentile, totalSaved: Math.round(totalSaved * 100) / 100 };
}

function PinnedCardWithHistory({
  pin,
  onPress,
}: {
  pin: PinnedItem;
  onPress: (itemId: string, itemName: string) => void;
}) {
  const { data: history } = useGetPriceHistoryQuery({ id: pin.item_id, days: 7 });
  return <PinnedProductCard item={pin} priceHistory={history ?? []} onPress={onPress} />;
}

export default function HomeScreen() {
  const { data: pins, isLoading } = useGetPinsQuery();
  const navigation = useNavigation<Nav>();
  const [prefSummary, setPrefSummary] = useState("");

  useEffect(() => {
    const loadPrefs = async () => {
      try {
        const raw = await AsyncStorage.getItem("@grocery_preferences");
        if (raw) {
          const prefs = JSON.parse(raw);
          const all = [...(prefs.dietary ?? []), ...(prefs.habits ?? [])];
          setPrefSummary(all.length ? all.join(", ") : "None set");
        } else {
          setPrefSummary("None set");
        }
      } catch {
        setPrefSummary("None set");
      }
    };
    const unsubscribe = navigation.addListener("focus", loadPrefs);
    return unsubscribe;
  }, [navigation]);

  const { percentile, totalSaved } = useMemo(
    () => calculateSavings(pins ?? []),
    [pins]
  );

  const handlePress = (itemId: string, itemName: string) => {
    navigation.navigate("ProductDetail", { itemId, itemName });
  };

  if (isLoading) {
    return (
      <LinearGradient colors={gradients.main} style={styles.center}>
        <ActivityIndicator size="large" color={colors.accent} />
      </LinearGradient>
    );
  }

  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const arcLength = circumference * 0.7;
  const gapLength = circumference * 0.3;
  const progressLength = arcLength * (1 - percentile / 100);

  return (
    <LinearGradient colors={gradients.main} style={{ flex: 1 }}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={styles.container}
      >
        {/* Savings Percentile Ring */}
        <View style={styles.ringSection}>
          <View style={styles.ringContainer}>
            <Svg width={160} height={180}>
              {/* Background arc (70%) */}
              <Circle
                cx={80}
                cy={80}
                r={radius}
                stroke={colors.bgCard}
                strokeWidth={12}
                fill="none"
                strokeDasharray={`${arcLength} ${gapLength}`}
                rotation={144}
                origin="80,80"
              />
              {/* Progress arc */}
              <Circle
                cx={80}
                cy={80}
                r={radius}
                stroke={colors.accent}
                strokeWidth={12}
                fill="none"
                strokeDasharray={`${progressLength} ${circumference - progressLength}`}
                strokeLinecap="round"
                rotation={144}
                origin="80,80"
              />
            </Svg>
            <View style={styles.ringTextOverlay}>
              <Text style={styles.ringPercentage}>Top {percentile}%</Text>
            </View>
          </View>
          <Text style={styles.ringSubtitle}>
            You are in the top {percentile}% of grocery shoppers
          </Text>
          <Text style={styles.savingsText}>
            Estimated savings: ${totalSaved.toFixed(2)}
          </Text>
        </View>

        {/* Preferences Card */}
        <TouchableOpacity
          style={styles.prefCard}
          activeOpacity={0.7}
          onPress={() => navigation.navigate("Preferences")}
        >
          <View style={styles.prefLeft}>
            <Text style={styles.prefIcon}>{"\u2699\uFE0F"}</Text>
            <Text style={styles.prefTitle}>Your Preferences</Text>
          </View>
          <View style={styles.prefRight}>
            <Text style={styles.prefSummary} numberOfLines={1}>
              {prefSummary}
            </Text>
            <Text style={styles.prefChevron}>{"\u203A"}</Text>
          </View>
        </TouchableOpacity>

        {/* Pinned Products */}
        <Text style={styles.sectionTitle}>Pinned Products</Text>
        {!pins?.length ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>
              Pin products from the Market tab to track them here
            </Text>
          </View>
        ) : (
          pins.map((pin) => (
            <PinnedCardWithHistory key={pin.id} pin={pin} onPress={handlePress} />
          ))
        )}

        <View style={{ height: 24 }} />
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { paddingTop: 12, paddingBottom: 24 },
  ringSection: {
    alignItems: "center",
    paddingVertical: 24,
    paddingHorizontal: 16,
  },
  ringContainer: {
    width: 160,
    height: 180,
    position: "relative",
  },
  ringTextOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: "center",
    alignItems: "center",
  },
  ringPercentage: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  ringSubtitle: {
    fontSize: 15,
    color: colors.textSecondary,
    marginTop: 12,
    textAlign: "center",
  },
  savingsText: {
    fontSize: 14,
    color: colors.textMuted,
    marginTop: 4,
  },
  prefCard: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: colors.bgCard,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginHorizontal: 16,
    marginTop: 8,
  },
  prefLeft: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  prefIcon: { fontSize: 20 },
  prefTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  prefRight: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    flexShrink: 1,
  },
  prefSummary: {
    fontSize: 13,
    color: colors.textSecondary,
    maxWidth: 140,
  },
  prefChevron: {
    fontSize: 22,
    color: colors.textMuted,
    fontWeight: "700",
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.textPrimary,
    paddingHorizontal: 16,
    paddingTop: 24,
    paddingBottom: 12,
  },
  emptyState: {
    padding: 40,
    alignItems: "center",
  },
  emptyText: {
    color: colors.textSecondary,
    fontSize: 14,
    textAlign: "center",
  },
});
