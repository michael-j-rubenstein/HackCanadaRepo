import React, { useMemo, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import GrocerySquareCard, { CARD_WIDTH } from "../components/GrocerySquareCard";
import GroceryItemCard from "../components/GroceryItemCard";
import { useGetCategoriesQuery, useGetItemsQuery } from "../../redux/api";
import type { GroceryItem } from "../types/models";
import type { HomeStackParamList } from "../routing/types";
import { colors, gradients } from "../theme/theme";
import { getCategoryEmoji } from "../utils/emojiMap";

type Nav = NativeStackNavigationProp<HomeStackParamList, "HomeList">;

const SNAP_INTERVAL = (CARD_WIDTH + 12) * 2;

type ActiveToggle = "drops" | "rises";

export default function HomeScreen() {
  const { data: categories, isLoading: catsLoading } = useGetCategoriesQuery();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | "all">("all");
  const [activeToggle, setActiveToggle] = useState<ActiveToggle>("drops");
  const navigation = useNavigation<Nav>();

  const {
    data: items,
    isLoading: itemsLoading,
    refetch,
  } = useGetItemsQuery(
    selectedCategoryId !== "all" ? { category_id: selectedCategoryId } : undefined
  );

  const mostActiveItems = useMemo(() => {
    if (!items) return [];
    if (activeToggle === "drops") {
      return items
        .filter((i) => (i.price_change_pct ?? 0) < 0)
        .sort((a, b) => (a.price_change_pct ?? 0) - (b.price_change_pct ?? 0))
        .slice(0, 10);
    }
    return items
      .filter((i) => (i.price_change_pct ?? 0) > 0)
      .sort((a, b) => (b.price_change_pct ?? 0) - (a.price_change_pct ?? 0))
      .slice(0, 10);
  }, [items, activeToggle]);

  const handlePress = (item: GroceryItem) => {
    navigation.navigate("ProductDetail", { itemId: item.id, itemName: item.name });
  };

  if (catsLoading) {
    return (
      <LinearGradient colors={gradients.main} style={styles.center}>
        <ActivityIndicator size="large" color={colors.accent} />
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={gradients.main} style={{ flex: 1 }}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={styles.container}
        refreshControl={
          <RefreshControl
            refreshing={itemsLoading}
            onRefresh={refetch}
            tintColor={colors.accent}
          />
        }
      >
        {/* Category Slider */}
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryRow}
        >
          <TouchableOpacity
            style={[
              styles.pill,
              selectedCategoryId === "all" ? styles.pillSelected : styles.pillUnselected,
            ]}
            onPress={() => setSelectedCategoryId("all")}
            activeOpacity={0.7}
          >
            <Text
              style={[
                styles.pillText,
                { color: selectedCategoryId === "all" ? colors.bgDeepest : colors.textSecondary },
              ]}
            >
              All
            </Text>
          </TouchableOpacity>
          {categories?.map((cat) => {
            const selected = cat.id === selectedCategoryId;
            return (
              <TouchableOpacity
                key={cat.id}
                style={[
                  styles.pill,
                  selected ? styles.pillSelected : styles.pillUnselected,
                ]}
                onPress={() => setSelectedCategoryId(cat.id)}
                activeOpacity={0.7}
              >
                <Text
                  style={[
                    styles.pillText,
                    { color: selected ? colors.bgDeepest : colors.textSecondary },
                  ]}
                >
                  {getCategoryEmoji(cat.name)} {cat.name}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>

        {/* Items Section */}
        {itemsLoading ? (
          <View style={styles.itemsLoading}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FlatList
            data={items}
            keyExtractor={(item) => String(item.id)}
            renderItem={({ item }) => (
              <GrocerySquareCard item={item} onPress={handlePress} />
            )}
            horizontal
            showsHorizontalScrollIndicator={false}
            snapToInterval={SNAP_INTERVAL}
            decelerationRate="fast"
            contentContainerStyle={styles.itemsRow}
            scrollEnabled
          />
        )}

        {/* Most Active Section */}
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Most Active</Text>
          <View style={styles.toggleRow}>
            {(["drops", "rises"] as const).map((t) => {
              const selected = activeToggle === t;
              return (
                <TouchableOpacity
                  key={t}
                  style={[
                    styles.pill,
                    selected ? styles.pillSelected : styles.pillUnselected,
                  ]}
                  onPress={() => setActiveToggle(t)}
                  activeOpacity={0.7}
                >
                  <Text
                    style={[
                      styles.pillText,
                      { color: selected ? colors.bgDeepest : colors.textSecondary },
                    ]}
                  >
                    {t === "drops" ? "Drops" : "Rises"}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {itemsLoading ? (
          <View style={styles.itemsLoading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : (
          mostActiveItems.map((item) => (
            <GroceryItemCard key={item.id} item={item} onPress={handlePress} />
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
  categoryRow: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    gap: 8,
  },
  pill: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 99,
  },
  pillSelected: {
    backgroundColor: colors.accent,
  },
  pillUnselected: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
  },
  pillText: {
    fontSize: 14,
    fontWeight: "600",
  },
  itemsRow: {
    paddingHorizontal: 16,
  },
  itemsLoading: {
    height: 200,
    justifyContent: "center",
    alignItems: "center",
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingTop: 24,
    paddingBottom: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  toggleRow: {
    flexDirection: "row",
    gap: 8,
  },
});
