import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, gradients } from "../theme/theme";
import { useRecipeSocket } from "../hooks/useRecipeSocket";

export default function RecipeScreen() {
  const [ingredientText, setIngredientText] = useState("");
  const {
    state,
    recipeMeta,
    currentStep,
    streamedText,
    statusMessage,
    error,
    isPlaying,
    startRecipe,
    completeStep,
    repeat,
    skip,
    goBack,
    stopAudio,
    reset,
  } = useRecipeSocket();

  const handleGenerate = () => {
    const ingredients = ingredientText
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (ingredients.length > 0) {
      startRecipe(ingredients);
    }
  };

  const handleTryAgain = () => {
    setIngredientText("");
    reset();
  };

  return (
    <LinearGradient colors={gradients.main} style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        {state === "idle" && (
          <View style={styles.section}>
            <Text style={styles.emoji}>{"\u{1F373}"}</Text>
            <Text style={styles.title}>Recipe Generator</Text>
            <Text style={styles.subtitle}>
              Enter your ingredients and we'll find a recipe with voice-guided
              cooking steps.
            </Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. chicken, rice, garlic, onion"
              placeholderTextColor={colors.textMuted}
              value={ingredientText}
              onChangeText={setIngredientText}
              multiline
            />
            <TouchableOpacity
              style={[
                styles.primaryButton,
                !ingredientText.trim() && styles.buttonDisabled,
              ]}
              onPress={handleGenerate}
              disabled={!ingredientText.trim()}
            >
              <Text style={styles.primaryButtonText}>Generate Recipe</Text>
            </TouchableOpacity>
          </View>
        )}

        {state === "loading" && (
          <View style={styles.section}>
            <ActivityIndicator size="large" color={colors.accent} />
            <Text style={styles.statusText}>{statusMessage}</Text>
            {recipeMeta && (
              <View style={styles.metaCard}>
                <Text style={styles.recipeTitle}>{recipeMeta.title}</Text>
                <Text style={styles.recipeSummary}>{recipeMeta.summary}</Text>
                <Text style={styles.stepCount}>
                  {recipeMeta.total_steps} steps
                </Text>
              </View>
            )}
          </View>
        )}

        {state === "cooking" && currentStep && (
          <View style={styles.section}>
            {recipeMeta && (
              <Text style={styles.recipeHeader}>{recipeMeta.title}</Text>
            )}

            <View style={styles.progressBar}>
              <View
                style={[
                  styles.progressFill,
                  {
                    width: `${
                      (currentStep.step_number / currentStep.total_steps) * 100
                    }%`,
                  },
                ]}
              />
            </View>
            <Text style={styles.progressText}>
              Step {currentStep.step_number} of {currentStep.total_steps}
            </Text>

            <View style={styles.stepCard}>
              <Text style={styles.stepTitle}>{currentStep.title}</Text>
              <Text style={styles.stepInstruction}>{streamedText}</Text>
            </View>

            <View style={styles.buttonRow}>
              <TouchableOpacity
                style={[
                  styles.secondaryButton,
                  currentStep.step_number <= 1 && styles.buttonDisabled,
                ]}
                onPress={goBack}
                disabled={currentStep.step_number <= 1}
              >
                <Text style={styles.secondaryButtonText}>Back</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.primaryButton}
                onPress={completeStep}
              >
                <Text style={styles.primaryButtonText}>Done</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.secondaryButton} onPress={skip}>
                <Text style={styles.secondaryButtonText}>Skip</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.audioRow}>
              {isPlaying ? (
                <TouchableOpacity
                  style={styles.audioButton}
                  onPress={stopAudio}
                >
                  <Text style={styles.audioButtonText}>Stop Audio</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity style={styles.audioButton} onPress={repeat}>
                  <Text style={styles.audioButtonText}>Replay</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}

        {state === "complete" && (
          <View style={styles.section}>
            <Text style={styles.celebrationEmoji}>{"\u{1F389}"}</Text>
            <Text style={styles.title}>Recipe Complete!</Text>
            <Text style={styles.subtitle}>
              Great job! Enjoy your meal.
            </Text>
            <TouchableOpacity
              style={styles.primaryButton}
              onPress={handleTryAgain}
            >
              <Text style={styles.primaryButtonText}>Cook Another</Text>
            </TouchableOpacity>
          </View>
        )}

        {state === "error" && (
          <View style={styles.section}>
            <Text style={styles.errorEmoji}>{"\u{26A0}\u{FE0F}"}</Text>
            <Text style={styles.title}>Something went wrong</Text>
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity
              style={styles.primaryButton}
              onPress={handleTryAgain}
            >
              <Text style={styles.primaryButtonText}>Try Again</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: {
    flexGrow: 1,
    justifyContent: "center",
    padding: 24,
  },
  section: { alignItems: "center" },
  emoji: { fontSize: 64, marginBottom: 16 },
  celebrationEmoji: { fontSize: 80, marginBottom: 16 },
  errorEmoji: { fontSize: 64, marginBottom: 16 },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: 8,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 15,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 22,
    marginBottom: 24,
  },
  input: {
    width: "100%",
    backgroundColor: colors.bgInput,
    borderRadius: 12,
    padding: 16,
    color: colors.textPrimary,
    fontSize: 16,
    minHeight: 80,
    textAlignVertical: "top",
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.border,
  },
  primaryButton: {
    backgroundColor: colors.accent,
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 12,
    minWidth: 80,
    alignItems: "center",
  },
  primaryButtonText: {
    color: colors.bgDeepest,
    fontWeight: "700",
    fontSize: 16,
  },
  secondaryButton: {
    backgroundColor: colors.bgCard,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 12,
    minWidth: 70,
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
    color: colors.textPrimary,
    fontWeight: "600",
    fontSize: 14,
  },
  buttonDisabled: { opacity: 0.4 },
  statusText: {
    fontSize: 16,
    color: colors.textSecondary,
    marginTop: 16,
    textAlign: "center",
  },
  metaCard: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 20,
    marginTop: 20,
    width: "100%",
    borderWidth: 1,
    borderColor: colors.border,
  },
  recipeTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: 8,
  },
  recipeSummary: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 8,
  },
  stepCount: {
    fontSize: 13,
    color: colors.accent,
    fontWeight: "600",
  },
  recipeHeader: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: 12,
    textAlign: "center",
  },
  progressBar: {
    width: "100%",
    height: 6,
    backgroundColor: colors.bgInput,
    borderRadius: 3,
    marginBottom: 8,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accent,
    borderRadius: 3,
  },
  progressText: {
    fontSize: 13,
    color: colors.textMuted,
    marginBottom: 16,
  },
  stepCard: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 20,
    width: "100%",
    marginBottom: 20,
    borderWidth: 1,
    borderColor: colors.border,
  },
  stepTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.accent,
    marginBottom: 12,
  },
  stepInstruction: {
    fontSize: 16,
    color: colors.textPrimary,
    lineHeight: 24,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 12,
  },
  audioRow: {
    flexDirection: "row",
    gap: 12,
  },
  audioButton: {
    backgroundColor: colors.bgCard,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.accent,
  },
  audioButtonText: {
    color: colors.accent,
    fontWeight: "600",
    fontSize: 14,
  },
  errorText: {
    fontSize: 14,
    color: colors.negative,
    textAlign: "center",
    marginBottom: 20,
    lineHeight: 20,
  },
});
