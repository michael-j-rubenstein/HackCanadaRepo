import React from "react";
import { StyleSheet, Text, View, TouchableOpacity } from "react-native";
import { useAuth0 } from "react-native-auth0";

export default function LoginScreen() {
  const { authorize } = useAuth0();

  const handleLogin = async () => {
    await authorize();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to HackCanadaRepo</Text>
      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>Log In</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 32,
  },
  button: {
    backgroundColor: "#007AFF",
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 8,
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "600",
  },
});
