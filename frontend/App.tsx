import React from "react";
import { StatusBar } from "react-native";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { NavigationContainer } from "@react-navigation/native";
import { store, persistor } from "./redux/store";
import { AuthProvider } from "./app/context/AuthContext";
import Router from "./app/routing/Router";

export default function App() {
  return (
    <AuthProvider>
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
          <NavigationContainer>
            <StatusBar barStyle="light-content" />
            <Router />
          </NavigationContainer>
        </PersistGate>
      </Provider>
    </AuthProvider>
  );
}
