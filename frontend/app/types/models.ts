export interface Category {
  id: string;
  name: string;
  icon: string | null;
}

export interface GroceryItem {
  id: string;
  name: string;
  brand: string | null;
  unit: string;
  category_id: string;
  category_name: string | null;
  current_price: number | null;
  price_change_pct: number | null;
}

export interface PricePoint {
  date: string;
  avg_price: number;
}

export interface ShoppingCartItem {
  id: string;
  item_id: string;
  item_name: string | null;
}

export interface ShoppingCartItemCreate {
  item_id: string;
}

export interface PinnedItem {
  id: string;
  item_id: string;
  item_name: string | null;
  current_price: number | null;
  price_change_pct: number | null;
}

export interface PinnedItemCreate {
  item_id: string;
}
