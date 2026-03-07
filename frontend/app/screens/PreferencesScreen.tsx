import React, { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, gradients } from "../theme/theme";

const STORAGE_KEY = "@grocery_preferences";

const DIETARY_OPTIONS = [
  "Vegan",
  "Vegetarian",
  "Gluten-Free",
  "Dairy-Free",
  "Nut-Free",
  "Halal",
  "Kosher",
  "None",
];

const HABIT_OPTIONS = [
  "Keto",
  "Paleo",
  "Low-Carb",
  "High-Protein",
  "Low-Sodium",
  "Organic",
  "None",
];

interface Prefs {
  dietary: string[];
  habits: string[];
}

export default function PreferencesScreen() {
  const [dietary, setDietary] = useState<string[]>([]);
  const [habits, setHabits] = useState<string[]>([]);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY).then((raw) => {
      if (raw) {
        const prefs: Prefs = JSON.parse(raw);
        setDietary(prefs.dietary ?? []);
        setHabits(prefs.habits ?? []);
      }
    });
  }, []);

  const save = (newDietary: string[], newHabits: string[]) => {
    const prefs: Prefs = { dietary: newDietary, habits: newHabits };
    AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  };

  const toggleDietary = (option: string) => {
    let next: string[];
    if (option === "None") {
      next = dietary.includes("None") ? [] : ["None"];
    } else {
      const without = dietary.filter((d) => d !== "None");
      next = without.includes(option)
        ? without.filter((d) => d !== option)
        : [...without, option];
    }
    setDietary(next);
    save(next, habits);
  };

  const toggleHabit = (option: string) => {
    let next: string[];
    if (option === "None") {
      next = habits.includes("None") ? [] : ["None"];
    } else {
      const without = habits.filter((h) => h !== "None");
      next = without.includes(option)
        ? without.filter((h) => h !== option)
        : [...without, option];
    }
    setHabits(next);
    save(dietary, next);
  };

  return (
    <LinearGradient colors={gradients.main} style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.sectionHeader}>Dietary Restrictions</Text>
        <View style={styles.chipContainer}>
          {DIETARY_OPTIONS.map((option) => {
            const selected = dietary.includes(option);
            return (
              <TouchableOpacity
                key={option}
                style={[styles.chip, selected && styles.chipSelected]}
                onPress={() => toggleDietary(option)}
                activeOpacity={0.7}
              >
                <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                  {option}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={styles.sectionHeader}>Diet Habits</Text>
        <View style={styles.chipContainer}>
          {HABIT_OPTIONS.map((option) => {
            const selected = habits.includes(option);
            return (
              <TouchableOpacity
                key={option}
                style={[styles.chip, selected && styles.chipSelected]}
                onPress={() => toggleHabit(option)}
                activeOpacity={0.7}
              >
                <Text style={[styles.chipText, selected && styles.chipTextSelected]}>
                  {option}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    paddingBottom: 40,
  },
  sectionHeader: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textPrimary,
    marginTop: 16,
    marginBottom: 12,
  },
  chipContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
  },
  chip: {
    backgroundColor: colors.bgCard,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  chipSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  chipText: {
    fontSize: 14,
    fontWeight: "500",
    color: colors.textSecondary,
  },
  chipTextSelected: {
    color: colors.bgDeepest,
    fontWeight: "600",
  },
});
