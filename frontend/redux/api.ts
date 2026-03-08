import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { BASE_URL } from "../config/api";
import type {
  Category,
  GroceryItem,
  PricePoint,
  ShoppingCartItem,
  ShoppingCartItemCreate,
  PinnedItem,
  PinnedItemCreate,
} from "../app/types/models";

export const groceryApi = createApi({
  reducerPath: "groceryApi",
  baseQuery: fetchBaseQuery({
    baseUrl: BASE_URL,
    prepareHeaders: (headers) => {
      headers.set("X-User-Id", "user_test1");
      return headers;
    },
  }),
  tagTypes: ["Items", "PriceHistory", "Cart", "Pins"],
  endpoints: (builder) => ({
    getCategories: builder.query<Category[], void>({
      query: () => "/categories",
    }),

    getItems: builder.query<
      GroceryItem[],
      { search?: string; category_id?: string; sort?: string } | void
    >({
      query: (params) => {
        const searchParams = new URLSearchParams();
        if (params && params.search) searchParams.set("search", params.search);
        if (params && params.category_id)
          searchParams.set("category_id", String(params.category_id));
        if (params && params.sort) searchParams.set("sort", params.sort);
        const qs = searchParams.toString();
        return `/items${qs ? `?${qs}` : ""}`;
      },
      providesTags: ["Items"],
    }),

    getItem: builder.query<GroceryItem, string>({
      query: (id) => `/items/${id}`,
      providesTags: (_result, _err, id) => [{ type: "Items", id }],
    }),

    getPriceHistory: builder.query<PricePoint[], { id: string; days?: number }>({
      query: ({ id, days = 30 }) => `/items/${id}/price-history?days=${days}`,
      providesTags: (_result, _err, { id }) => [{ type: "PriceHistory", id }],
    }),

    getCart: builder.query<ShoppingCartItem[], void>({
      query: () => "/cart",
      providesTags: ["Cart"],
    }),

    addToCart: builder.mutation<ShoppingCartItem, ShoppingCartItemCreate>({
      query: (body) => ({
        url: "/cart",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Cart"],
    }),

    removeFromCart: builder.mutation<void, string>({
      query: (itemId) => ({
        url: `/cart/${itemId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Cart"],
    }),

    getPins: builder.query<PinnedItem[], void>({
      query: () => "/pins",
      providesTags: ["Pins"],
    }),

    pinItem: builder.mutation<PinnedItem, PinnedItemCreate>({
      query: (body) => ({
        url: "/pins",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Pins"],
    }),

    unpinItem: builder.mutation<void, string>({
      query: (itemId) => ({
        url: `/pins/${itemId}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Pins"],
    }),
  }),
});

export const {
  useGetCategoriesQuery,
  useGetItemsQuery,
  useGetItemQuery,
  useGetPriceHistoryQuery,
  useGetCartQuery,
  useAddToCartMutation,
  useRemoveFromCartMutation,
  useGetPinsQuery,
  usePinItemMutation,
  useUnpinItemMutation,
} = groceryApi;
