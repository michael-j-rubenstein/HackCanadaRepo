import React, { useState, useRef, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Image,
  ScrollView,
  ActivityIndicator,
  Alert,
  TextInput,
  Platform,
  Animated,
} from "react-native";
import { CameraView, CameraType, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import * as FileSystem from "expo-file-system/legacy";
import { colors } from "../theme/theme";
import {
  useScanReceiptBase64Mutation,
  useSubmitReceiptMutation,
} from "../../redux/api";
import type { MatchedItem, ReceiptItem } from "../types/models";

type Mode = "camera" | "preview" | "results" | "manual";

interface EditableItem {
  receipt_item: ReceiptItem;
  product_id: string | null;
  product_name: string | null;
  price: number;
  selected: boolean;
}

export default function ReportScreen() {
  const [mode, setMode] = useState<Mode>("camera");
  const [permission, requestPermission] = useCameraPermissions();
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [editableItems, setEditableItems] = useState<EditableItem[]>([]);
  const [storeName, setStoreName] = useState<string | null>(null);
  const [receiptDate, setReceiptDate] = useState<string | null>(null);
  const [total, setTotal] = useState<number | null>(null);
  const cameraRef = useRef<CameraView>(null);

  const [scanReceipt, { isLoading: isScanning }] = useScanReceiptBase64Mutation();
  const [submitReceipt, { isLoading: isSubmitting }] = useSubmitReceiptMutation();

  // Scan line animation
  const scanLineAnim = useRef(new Animated.Value(0)).current;
  const [imageContainerHeight, setImageContainerHeight] = useState(400);

  useEffect(() => {
    if (isScanning) {
      const animation = Animated.loop(
        Animated.sequence([
          Animated.timing(scanLineAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(scanLineAnim, {
            toValue: 0,
            duration: 1500,
            useNativeDriver: true,
          }),
        ])
      );
      animation.start();
      return () => animation.stop();
    }
  }, [isScanning]);

  // Manual entry state
  const [manualItems, setManualItems] = useState<{ name: string; price: string }[]>([
    { name: "", price: "" },
  ]);
  const [manualStore, setManualStore] = useState("");

  if (!permission) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Camera Permission Required</Text>
        <Text style={styles.subtitle}>
          We need camera access to scan receipts
        </Text>
        <TouchableOpacity style={styles.button} onPress={requestPermission}>
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: false,
        });
        if (photo?.uri) {
          setImageUri(photo.uri);
          setMode("preview");
        }
      } catch (error) {
        Alert.alert("Error", "Failed to take picture");
      }
    }
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setImageUri(result.assets[0].uri);
      setMode("preview");
    }
  };

  const handleScan = async () => {
    if (!imageUri) return;
    console.log("[SCAN] Step 1: Starting scan with URI:", imageUri);

    try {
      console.log("[SCAN] Step 2: Reading file as base64...");
      console.log("[SCAN] Step 2a: Checking file info...");
      const fileInfo = await FileSystem.getInfoAsync(imageUri);
      console.log("[SCAN] Step 2b: File info:", JSON.stringify(fileInfo));

      if (!fileInfo.exists) {
        throw new Error("File does not exist at URI");
      }

      console.log("[SCAN] Step 2c: Starting base64 read...");
      const base64Data = await FileSystem.readAsStringAsync(imageUri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      console.log("[SCAN] Step 3: Base64 read success, length:", base64Data.length);

      const filename = imageUri.split("/").pop() || "receipt.jpg";
      const match = /\.(\w+)$/.exec(filename);
      const ext = match ? match[1].toLowerCase() : "jpeg";
      // webp needs special handling for mime type
      const mimeType = ext === "webp" ? "image/webp" : `image/${ext}`;
      console.log("[SCAN] Step 4: Filename:", filename, "Extension:", ext, "MimeType:", mimeType);

      console.log("[SCAN] Step 5: Calling API...");
      const result = await scanReceipt({
        image_base64: base64Data,
        mime_type: mimeType,
      }).unwrap();
      console.log("[SCAN] Step 6: API success, items:", result.matched_items?.length);
      console.log("[SCAN] Extracted items:", result.matched_items.map(m => m.receipt_item.name));
      console.log("[SCAN] Unmatched items:", result.unmatched_items.map(i => i.name));

      const items: EditableItem[] = result.matched_items.map((m) => ({
        receipt_item: m.receipt_item,
        product_id: m.product_id,
        product_name: m.product_name,
        price: m.receipt_item.total_price,
        selected: m.confidence >= 0.7,
      }));

      result.unmatched_items.forEach((item) => {
        items.push({
          receipt_item: item,
          product_id: null,
          product_name: null,
          price: item.total_price,
          selected: false,
        });
      });

      setEditableItems(items);
      setStoreName(result.store_name);
      setReceiptDate(result.date);
      setTotal(result.total);
      setMode("results");
    } catch (error) {
      console.error("[SCAN] ERROR:", error);
      Alert.alert("Scan Failed", "Could not extract receipt data. Try again or use manual entry.");
    }
  };

  const toggleItemSelection = (index: number) => {
    setEditableItems((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, selected: !item.selected } : item
      )
    );
  };

  const updateItemPrice = (index: number, price: string) => {
    const numPrice = parseFloat(price) || 0;
    setEditableItems((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, price: numPrice } : item
      )
    );
  };

  const handleConfirm = async () => {
    const selectedItems = editableItems.filter(
      (item) => item.selected && item.product_id
    );

    if (selectedItems.length === 0) {
      Alert.alert("No Items", "Please select at least one matched item to submit.");
      return;
    }

    try {
      await submitReceipt({
        store_name: storeName,
        date: receiptDate,
        items: selectedItems.map((item) => ({
          product_id: item.product_id!,
          price: item.price,
        })),
      }).unwrap();

      Alert.alert("Success", `Submitted ${selectedItems.length} items!`);
      resetState();
    } catch (error) {
      Alert.alert("Error", "Failed to submit receipt");
    }
  };

  const handleManualSubmit = async () => {
    const validItems = manualItems.filter(
      (item) => item.name.trim() && parseFloat(item.price) > 0
    );

    if (validItems.length === 0) {
      Alert.alert("No Items", "Please add at least one item with a price.");
      return;
    }

    Alert.alert(
      "Manual Entry",
      "Manual entries require product matching. This feature is coming soon.",
      [{ text: "OK", onPress: resetState }]
    );
  };

  const addManualItem = () => {
    setManualItems((prev) => [...prev, { name: "", price: "" }]);
  };

  const updateManualItem = (index: number, field: "name" | "price", value: string) => {
    setManualItems((prev) =>
      prev.map((item, i) =>
        i === index ? { ...item, [field]: value } : item
      )
    );
  };

  const resetState = () => {
    setMode("camera");
    setImageUri(null);
    setEditableItems([]);
    setStoreName(null);
    setReceiptDate(null);
    setTotal(null);
    setManualItems([{ name: "", price: "" }]);
    setManualStore("");
  };

  // Camera Mode
  if (mode === "camera") {
    return (
      <View style={styles.container}>
        <CameraView
          ref={cameraRef}
          style={styles.camera}
          facing="back"
        >
          <View style={styles.cameraOverlay}>
            <View style={styles.scanFrame} />
            <Text style={styles.scanHint}>Position receipt within frame</Text>
          </View>
        </CameraView>

        <View style={styles.controls}>
          <TouchableOpacity style={styles.controlButton} onPress={pickImage}>
            <Text style={styles.controlIcon}>🖼️</Text>
            <Text style={styles.controlLabel}>Album</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
            <View style={styles.captureInner} />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.controlButton}
            onPress={() => setMode("manual")}
          >
            <Text style={styles.controlIcon}>✏️</Text>
            <Text style={styles.controlLabel}>Manual</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Preview Mode
  if (mode === "preview") {
    return (
      <View style={styles.container}>
        <View
          style={styles.imageContainer}
          onLayout={(e) => setImageContainerHeight(e.nativeEvent.layout.height)}
        >
          {imageUri && (
            <Image source={{ uri: imageUri }} style={styles.previewImage} />
          )}
          {isScanning && (
            <Animated.View
              style={[
                styles.scanLine,
                {
                  transform: [
                    {
                      translateY: scanLineAnim.interpolate({
                        inputRange: [0, 1],
                        outputRange: [0, imageContainerHeight - 3],
                      }),
                    },
                  ],
                },
              ]}
            />
          )}
        </View>

        <View style={styles.previewControls}>
          {isScanning ? (
            <View style={styles.scanningContainer}>
              <ActivityIndicator size="large" color={colors.accent} />
              <Text style={styles.scanningText}>Scanning receipt...</Text>
            </View>
          ) : (
            <>
              <TouchableOpacity
                style={[styles.button, styles.secondaryButton]}
                onPress={resetState}
              >
                <Text style={styles.secondaryButtonText}>Retake</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.button} onPress={handleScan}>
                <Text style={styles.buttonText}>Scan</Text>
              </TouchableOpacity>
            </>
          )}
        </View>
      </View>
    );
  }

  // Results Mode
  if (mode === "results") {
    const selectedCount = editableItems.filter((i) => i.selected && i.product_id).length;

    return (
      <View style={styles.container}>
        <View style={styles.resultsHeader}>
          <Text style={styles.resultsTitle}>Scanned Items</Text>
          {storeName && <Text style={styles.storeName}>{storeName}</Text>}
          {receiptDate && <Text style={styles.receiptDate}>{receiptDate}</Text>}
        </View>

        <ScrollView style={styles.itemsList}>
          {editableItems.map((item, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.itemCard,
                item.selected && styles.itemCardSelected,
                !item.product_id && styles.itemCardUnmatched,
              ]}
              onPress={() => item.product_id && toggleItemSelection(index)}
            >
              <View style={styles.itemCheckbox}>
                {item.selected && item.product_id && (
                  <Text style={styles.checkmark}>✓</Text>
                )}
              </View>
              <View style={styles.itemInfo}>
                <Text style={styles.itemName}>{item.receipt_item.name}</Text>
                {item.product_id ? (
                  <Text style={styles.matchedTo}>
                    → {item.product_name}
                  </Text>
                ) : (
                  <Text style={styles.unmatched}>No match found</Text>
                )}
              </View>
              <TextInput
                style={styles.priceInput}
                value={item.price.toFixed(2)}
                onChangeText={(val) => updateItemPrice(index, val)}
                keyboardType="decimal-pad"
                editable={item.selected}
              />
            </TouchableOpacity>
          ))}
        </ScrollView>

        {total !== null && (
          <View style={styles.totalRow}>
            <Text style={styles.totalLabel}>Receipt Total:</Text>
            <Text style={styles.totalValue}>${total.toFixed(2)}</Text>
          </View>
        )}

        <View style={styles.resultsControls}>
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={resetState}
          >
            <Text style={styles.secondaryButtonText}>Cancel</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, selectedCount === 0 && styles.buttonDisabled]}
            onPress={handleConfirm}
            disabled={isSubmitting || selectedCount === 0}
          >
            {isSubmitting ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <Text style={styles.buttonText}>
                Confirm ({selectedCount})
              </Text>
            )}
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // Manual Entry Mode
  return (
    <View style={styles.container}>
      <View style={styles.manualHeader}>
        <Text style={styles.resultsTitle}>Manual Entry</Text>
        <TouchableOpacity onPress={resetState}>
          <Text style={styles.cancelText}>Cancel</Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.manualForm}>
        <TextInput
          style={styles.input}
          placeholder="Store name (optional)"
          placeholderTextColor={colors.textMuted}
          value={manualStore}
          onChangeText={setManualStore}
        />

        <Text style={styles.sectionLabel}>Items</Text>
        {manualItems.map((item, index) => (
          <View key={index} style={styles.manualItemRow}>
            <TextInput
              style={[styles.input, styles.itemNameInput]}
              placeholder="Item name"
              placeholderTextColor={colors.textMuted}
              value={item.name}
              onChangeText={(val) => updateManualItem(index, "name", val)}
            />
            <TextInput
              style={[styles.input, styles.itemPriceInput]}
              placeholder="$0.00"
              placeholderTextColor={colors.textMuted}
              value={item.price}
              onChangeText={(val) => updateManualItem(index, "price", val)}
              keyboardType="decimal-pad"
            />
          </View>
        ))}

        <TouchableOpacity style={styles.addItemButton} onPress={addManualItem}>
          <Text style={styles.addItemText}>+ Add Item</Text>
        </TouchableOpacity>
      </ScrollView>

      <View style={styles.resultsControls}>
        <TouchableOpacity style={styles.button} onPress={handleManualSubmit}>
          <Text style={styles.buttonText}>Submit</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgDeepest,
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  scanFrame: {
    width: 280,
    height: 400,
    borderWidth: 2,
    borderColor: colors.accent,
    borderRadius: 12,
    backgroundColor: "transparent",
  },
  scanHint: {
    color: colors.textSecondary,
    marginTop: 16,
    fontSize: 14,
  },
  controls: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingVertical: 24,
    backgroundColor: colors.bgSection,
  },
  controlButton: {
    alignItems: "center",
    padding: 12,
  },
  controlIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  controlLabel: {
    color: colors.textSecondary,
    fontSize: 12,
  },
  captureButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.accent,
    justifyContent: "center",
    alignItems: "center",
  },
  captureInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: colors.accent,
    borderWidth: 3,
    borderColor: colors.bgDeepest,
  },
  imageContainer: {
    flex: 1,
    position: "relative",
  },
  previewImage: {
    flex: 1,
    resizeMode: "contain",
  },
  scanLine: {
    position: "absolute",
    left: 20,
    right: 20,
    height: 3,
    backgroundColor: colors.accent,
    shadowColor: colors.accent,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 10,
    elevation: 5,
  },
  previewControls: {
    flexDirection: "row",
    justifyContent: "space-around",
    padding: 24,
    backgroundColor: colors.bgSection,
  },
  scanningContainer: {
    alignItems: "center",
    padding: 20,
  },
  scanningText: {
    color: colors.textPrimary,
    marginTop: 12,
    fontSize: 16,
  },
  button: {
    backgroundColor: colors.accent,
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 8,
    minWidth: 120,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  secondaryButton: {
    backgroundColor: colors.bgCard,
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: 8,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: 24,
  },
  resultsHeader: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  resultsTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  storeName: {
    fontSize: 14,
    color: colors.accent,
    marginTop: 4,
  },
  receiptDate: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2,
  },
  itemsList: {
    flex: 1,
    padding: 16,
  },
  itemCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.bgCard,
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  itemCardSelected: {
    borderColor: colors.accent,
    backgroundColor: "rgba(0, 212, 170, 0.1)",
  },
  itemCardUnmatched: {
    opacity: 0.6,
  },
  itemCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.accent,
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  checkmark: {
    color: colors.accent,
    fontSize: 14,
    fontWeight: "bold",
  },
  itemInfo: {
    flex: 1,
  },
  itemName: {
    fontSize: 15,
    color: colors.textPrimary,
    fontWeight: "500",
  },
  matchedTo: {
    fontSize: 12,
    color: colors.accent,
    marginTop: 2,
  },
  unmatched: {
    fontSize: 12,
    color: colors.negative,
    marginTop: 2,
  },
  priceInput: {
    backgroundColor: colors.bgInput,
    borderRadius: 6,
    paddingHorizontal: 10,
    paddingVertical: 6,
    color: colors.textPrimary,
    fontSize: 14,
    width: 70,
    textAlign: "right",
  },
  totalRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  totalLabel: {
    fontSize: 16,
    color: colors.textSecondary,
  },
  totalValue: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  resultsControls: {
    flexDirection: "row",
    justifyContent: "space-around",
    padding: 20,
    backgroundColor: colors.bgSection,
  },
  manualHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  cancelText: {
    color: colors.accent,
    fontSize: 16,
  },
  manualForm: {
    flex: 1,
    padding: 20,
  },
  input: {
    backgroundColor: colors.bgInput,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: colors.textPrimary,
    fontSize: 16,
    marginBottom: 12,
  },
  sectionLabel: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 8,
    marginBottom: 12,
  },
  manualItemRow: {
    flexDirection: "row",
    gap: 10,
  },
  itemNameInput: {
    flex: 2,
  },
  itemPriceInput: {
    flex: 1,
  },
  addItemButton: {
    padding: 12,
    alignItems: "center",
  },
  addItemText: {
    color: colors.accent,
    fontSize: 15,
    fontWeight: "500",
  },
});
