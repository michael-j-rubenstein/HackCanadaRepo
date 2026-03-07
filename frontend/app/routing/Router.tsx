import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useAuth0 } from "react-native-auth0";
import HomeScreen from "../screens/HomeScreen";
import LoginScreen from "../screens/LoginScreen";

const Stack = createNativeStackNavigator();

export default function Router() {
  const { user } = useAuth0();
  const isAuthenticated = user !== undefined && user !== null;

  return (
    <Stack.Navigator>
      {isAuthenticated ? (
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: "HackCanadaRepo" }}
        />
      ) : (
        <Stack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
      )}
    </Stack.Navigator>
  );
}
