import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text } from "react-native";
import { useAuth } from "../context/AuthContext";

import HomeScreen from "../screens/HomeScreen";
import MarketScreen from "../screens/MarketScreen";
import ProductDetailScreen from "../screens/ProductDetailScreen";
import ShoppingCartScreen from "../screens/ShoppingCartScreen";
import ReportScreen from "../screens/ReportScreen";
import RecipeScreen from "../screens/RecipeScreen";
import PreferencesScreen from "../screens/PreferencesScreen";
import LoginScreen from "../screens/LoginScreen";
import SignUpScreen from "../screens/SignUpScreen";

import type { HomeStackParamList, MarketStackParamList, TabParamList } from "./types";
import { colors } from "../theme/theme";

const HomeStackNav = createNativeStackNavigator<HomeStackParamList>();
const MarketStackNav = createNativeStackNavigator<MarketStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();
const AuthStack = createNativeStackNavigator();

function HomeStackScreen() {
  return (
    <HomeStackNav.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.bgDeepest },
        headerTintColor: colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <HomeStackNav.Screen
        name="HomeDashboard"
        component={HomeScreen}
        options={{ title: "Home" }}
      />
      <HomeStackNav.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ route }) => ({ title: route.params.itemName })}
      />
      <HomeStackNav.Screen
        name="Preferences"
        component={PreferencesScreen}
        options={{ title: "Preferences" }}
      />
    </HomeStackNav.Navigator>
  );
}

function MarketStackScreen() {
  return (
    <MarketStackNav.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.bgDeepest },
        headerTintColor: colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <MarketStackNav.Screen
        name="MarketList"
        component={MarketScreen}
        options={{ title: "Grocery Market" }}
      />
      <MarketStackNav.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ route }) => ({ title: route.params.itemName })}
      />
    </MarketStackNav.Navigator>
  );
}

const tabIcons: Record<string, string> = {
  HomeTab: "\u{1F3E0}",
  MarketTab: "\u{1F3EA}",
  CartTab: "\u{1F6D2}",
  ReportTab: "\u{1F4CA}",
  RecipeTab: "\u{1F373}",
};

export default function Router() {
  const { user } = useAuth();
  const isAuthenticated = user !== null;

  if (!isAuthenticated) {
    return (
      <AuthStack.Navigator>
        <AuthStack.Screen
          name="Login"
          component={LoginScreen}
          options={{ headerShown: false }}
        />
        <AuthStack.Screen
          name="SignUp"
          component={SignUpScreen}
          options={{ headerShown: false }}
        />
      </AuthStack.Navigator>
    );
  }

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: route.name !== "HomeTab" && route.name !== "MarketTab",
        headerStyle: { backgroundColor: colors.bgDeepest },
        headerTintColor: colors.textPrimary,
        headerShadowVisible: false,
        tabBarIcon: ({ size }) => (
          <Text style={{ fontSize: size }}>{tabIcons[route.name] ?? "?"}</Text>
        ),
        tabBarActiveTintColor: colors.tabBarActive,
        tabBarInactiveTintColor: colors.tabBarInactive,
        tabBarStyle: {
          backgroundColor: colors.tabBarBg,
          borderTopColor: colors.bgCard,
          borderTopWidth: 1,
        },
      })}
    >
      <Tab.Screen name="HomeTab" component={HomeStackScreen} options={{ title: "Home" }} />
      <Tab.Screen name="MarketTab" component={MarketStackScreen} options={{ title: "Market" }} />
      <Tab.Screen name="CartTab" component={ShoppingCartScreen} options={{ title: "Cart" }} />
      <Tab.Screen name="ReportTab" component={ReportScreen} options={{ title: "Report" }} />
      <Tab.Screen name="RecipeTab" component={RecipeScreen} options={{ title: "Recipe" }} />
    </Tab.Navigator>
  );
}
