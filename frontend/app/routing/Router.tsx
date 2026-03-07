import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { Text } from "react-native";

import HomeScreen from "../screens/HomeScreen";
import ProductDetailScreen from "../screens/ProductDetailScreen";
import ShoppingCartScreen from "../screens/ShoppingCartScreen";
import ReportScreen from "../screens/ReportScreen";
import RecipeScreen from "../screens/RecipeScreen";

import type { HomeStackParamList, TabParamList } from "./types";
import { colors } from "../theme/theme";

const HomeStack = createNativeStackNavigator<HomeStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

function HomeStackScreen() {
  return (
    <HomeStack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: colors.bgDeepest },
        headerTintColor: colors.textPrimary,
        headerShadowVisible: false,
      }}
    >
      <HomeStack.Screen
        name="HomeList"
        component={HomeScreen}
        options={{ title: "Grocery Market" }}
      />
      <HomeStack.Screen
        name="ProductDetail"
        component={ProductDetailScreen}
        options={({ route }) => ({ title: route.params.itemName })}
      />
    </HomeStack.Navigator>
  );
}

const tabIcons: Record<string, string> = {
  HomeTab: "\u{1F3E0}",
  CartTab: "\u{1F6D2}",
  ReportTab: "\u{1F4CA}",
  RecipeTab: "\u{1F373}",
};

export default function Router() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: route.name !== "HomeTab",
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
      <Tab.Screen name="CartTab" component={ShoppingCartScreen} options={{ title: "Cart" }} />
      <Tab.Screen name="ReportTab" component={ReportScreen} options={{ title: "Report" }} />
      <Tab.Screen name="RecipeTab" component={RecipeScreen} options={{ title: "Recipe" }} />
    </Tab.Navigator>
  );
}
