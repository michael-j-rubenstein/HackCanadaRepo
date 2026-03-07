import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, gradients } from "../theme/theme";

export default function RecipeScreen() {
  return (
    <LinearGradient colors={gradients.main} style={styles.container}>
      <Text style={styles.emoji}>{"\u{1F373}"}</Text>
      <Text style={styles.title}>Recipes coming soon</Text>
      <Text style={styles.subtitle}>Stay tuned for smart recipe suggestions based on your grocery prices.</Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center", padding: 32 },
  emoji: { fontSize: 64, marginBottom: 16 },
  title: { fontSize: 22, fontWeight: "700", color: colors.textPrimary, marginBottom: 8 },
  subtitle: { fontSize: 15, color: colors.textSecondary, textAlign: "center", lineHeight: 22 },
});
