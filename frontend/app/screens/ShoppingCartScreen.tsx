import React, { useCallback, useMemo, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import {
  useGetCartQuery,
  useAddToCartMutation,
  useRemoveFromCartMutation,
  useGetItemsQuery,
} from "../../redux/api";
import { colors, gradients } from "../theme/theme";
import { getItemEmoji } from "../utils/emojiMap";

export default function ShoppingCartScreen() {
  const { data: cartItems, isLoading: cartLoading } = useGetCartQuery();
  const [addToCart] = useAddToCartMutation();
  const [removeFromCart] = useRemoveFromCartMutation();

  const [tab, setTab] = useState<"cart" | "add">("cart");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [debounceTimer, setDebounceTimer] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  const handleSearchChange = useCallback(
    (text: string) => {
      setSearch(text);
      if (debounceTimer) clearTimeout(debounceTimer);
      const timer = setTimeout(() => setDebouncedSearch(text.trim()), 300);
      setDebounceTimer(timer);
    },
    [debounceTimer]
  );

  const { data: allItems, isFetching: itemsLoading } = useGetItemsQuery(
    debouncedSearch ? { search: debouncedSearch } : undefined
  );

  const cartItemIds = useMemo(() => {
    const s = new Set<number>();
    cartItems?.forEach((ci) => s.add(ci.item_id));
    return s;
  }, [cartItems]);

  const filteredResults = useMemo(() => {
    if (!allItems) return [];
    return allItems.filter((item) => !cartItemIds.has(item.id));
  }, [allItems, cartItemIds]);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleAddToCart = async () => {
    const ids = Array.from(selectedIds);
    for (const id of ids) {
      try {
        await addToCart({ item_id: id }).unwrap();
      } catch {
        // skip duplicates / errors
      }
    }
    setSelectedIds(new Set());
  };

  return (
    <LinearGradient colors={gradients.main} style={{ flex: 1 }}>
      <FlatList
        data={[]}
        renderItem={null}
        ListHeaderComponent={
          <>
            {/* Toggle */}
            <View style={styles.toggleRow}>
              {(["cart", "add"] as const).map((t) => {
                const selected = tab === t;
                return (
                  <TouchableOpacity
                    key={t}
                    style={[styles.pill, selected ? styles.pillSelected : styles.pillUnselected]}
                    onPress={() => setTab(t)}
                    activeOpacity={0.7}
                  >
                    <Text style={[styles.pillText, { color: selected ? colors.bgDeepest : colors.textSecondary }]}>
                      {t === "cart" ? "Your Cart" : "Add Items"}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>

            {tab === "cart" ? (
              <>
                {cartLoading ? (
                  <ActivityIndicator
                    size="small"
                    color={colors.accent}
                    style={{ marginVertical: 16 }}
                  />
                ) : !cartItems?.length ? (
                  <Text style={styles.emptyText}>Your cart is empty</Text>
                ) : (
                  cartItems.map((ci) => (
                    <View key={ci.id} style={styles.cartRow}>
                      <Text style={styles.cartItemName}>
                        {ci.item_name ?? `Item #${ci.item_id}`}
                      </Text>
                      <TouchableOpacity
                        onPress={() => removeFromCart(ci.item_id)}
                        style={styles.removeBtn}
                      >
                        <Text style={styles.removeBtnText}>Remove</Text>
                      </TouchableOpacity>
                    </View>
                  ))
                )}
              </>
            ) : (
              <>
                <TextInput
                  style={styles.searchInput}
                  placeholder="Search items..."
                  placeholderTextColor={colors.textSecondary}
                  value={search}
                  onChangeText={handleSearchChange}
                />

                {itemsLoading ? (
                  <ActivityIndicator
                    size="small"
                    color={colors.accent}
                    style={{ marginVertical: 12 }}
                  />
                ) : filteredResults.length === 0 ? (
                  <Text style={styles.emptyText}>No items found</Text>
                ) : (
                  filteredResults.map((item) => {
                    const isSelected = selectedIds.has(item.id);
                    return (
                      <TouchableOpacity
                        key={item.id}
                        style={[styles.itemRow, isSelected && styles.itemRowSelected]}
                        onPress={() => toggleSelect(item.id)}
                      >
                        <Text style={styles.itemEmoji}>
                          {getItemEmoji(item.name, item.category_name)}
                        </Text>
                        <Text
                          style={[styles.itemText, isSelected && styles.itemTextSelected]}
                        >
                          {item.name}
                        </Text>
                        <Text
                          style={[styles.itemPrice, isSelected && styles.itemTextSelected]}
                        >
                          ${item.current_price?.toFixed(2) ?? "\u2014"}
                        </Text>
                      </TouchableOpacity>
                    );
                  })
                )}
              </>
            )}

            <View style={{ height: 80 }} />
          </>
        }
        keyExtractor={() => "header"}
      />
      {selectedIds.size > 0 && (
        <TouchableOpacity style={styles.fab} onPress={handleAddToCart}>
          <Text style={styles.fabText}>
            Add to Shopping Cart ({selectedIds.size})
          </Text>
        </TouchableOpacity>
      )}
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  toggleRow: {
    flexDirection: "row",
    gap: 8,
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 12,
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
  emptyText: {
    color: colors.textSecondary,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 14,
  },
  cartRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginVertical: 2,
    borderRadius: 8,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cartItemName: {
    fontSize: 15,
    color: colors.textPrimary,
    flex: 1,
  },
  removeBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: "#ff4d4f22",
  },
  removeBtnText: {
    color: "#ff4d4f",
    fontSize: 13,
    fontWeight: "600",
  },
  searchInput: {
    marginHorizontal: 16,
    marginBottom: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 8,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
    color: colors.textPrimary,
    fontSize: 15,
  },
  itemRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginHorizontal: 16,
    marginVertical: 2,
    borderRadius: 8,
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
  },
  itemRowSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  itemEmoji: { fontSize: 20, marginRight: 10 },
  itemText: { fontSize: 15, color: colors.textPrimary, flex: 1 },
  itemPrice: { fontSize: 15, color: colors.textSecondary },
  itemTextSelected: { color: colors.bgDeepest, fontWeight: "600" },
  fab: {
    position: "absolute",
    bottom: 24,
    right: 16,
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderRadius: 28,
    backgroundColor: colors.accent,
    elevation: 6,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  fabText: {
    color: colors.bgDeepest,
    fontSize: 15,
    fontWeight: "700",
  },
});
