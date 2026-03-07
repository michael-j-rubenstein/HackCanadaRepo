export interface Category {
  id: number;
  name: string;
  icon: string | null;
}

export interface GroceryItem {
  id: number;
  name: string;
  brand: string | null;
  unit: string;
  image_url: string | null;
  category_id: number;
  category_name: string | null;
  current_price: number | null;
  price_change_pct: number | null;
  external_id: string | null;
  created_at: string | null;
}

export interface PricePoint {
  date: string;
  avg_price: number;
}

export interface PriceSubmission {
  id: number;
  item_id: number;
  price: number;
  store_name: string;
  date_observed: string;
  submitted_at: string | null;
}

export interface PriceSubmissionCreate {
  price: number;
  store_name: string;
  date_observed: string;
}

export interface PriceAlert {
  id: number;
  item_id: number;
  item_name: string | null;
  target_price: number;
  is_triggered: boolean;
  triggered_at: string | null;
  created_at: string | null;
}

export interface PriceAlertCreate {
  item_id: number;
  target_price: number;
}
