export type HomeStackParamList = {
  HomeDashboard: undefined;
  ProductDetail: { itemId: string; itemName: string };
  Preferences: undefined;
};

export type MarketStackParamList = {
  MarketList: undefined;
  ProductDetail: { itemId: string; itemName: string };
};

export type TabParamList = {
  HomeTab: undefined;
  MarketTab: undefined;
  CartTab: undefined;
  ReportTab: undefined;
  RecipeTab: undefined;
};
