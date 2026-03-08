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

// Receipt types
export interface ReceiptItem {
  name: string;
  total_price: number;
  category: string | null;
  weight_value: number | null;
  weight_unit: string | null;
}

export interface MatchedItem {
  receipt_item: ReceiptItem;
  product_id: string | null;
  product_name: string | null;
  confidence: number;
}

export interface ScanResponse {
  store_name: string | null;
  date: string | null;
  matched_items: MatchedItem[];
  unmatched_items: ReceiptItem[];
  subtotal: number | null;
  tax: number | null;
  total: number | null;
}

export interface SubmitItem {
  product_id: string;
  price: number;
}

export interface SubmitRequest {
  store_name: string | null;
  date: string | null;
  items: SubmitItem[];
}

export interface SubmitResponse {
  submission_id: string;
  items_count: number;
}
