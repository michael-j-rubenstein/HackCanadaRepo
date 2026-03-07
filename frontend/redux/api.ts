import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { BASE_URL } from "../config/api";
import type {
  Category,
  GroceryItem,
  PricePoint,
  PriceSubmission,
  PriceSubmissionCreate,
  PriceAlert,
  PriceAlertCreate,
} from "../app/types/models";

export const groceryApi = createApi({
  reducerPath: "groceryApi",
  baseQuery: fetchBaseQuery({ baseUrl: BASE_URL }),
  tagTypes: ["Items", "Alerts", "PriceHistory"],
  endpoints: (builder) => ({
    getCategories: builder.query<Category[], void>({
      query: () => "/categories",
    }),

    getItems: builder.query<
      GroceryItem[],
      { search?: string; category_id?: number; sort?: string } | void
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

    getItem: builder.query<GroceryItem, number>({
      query: (id) => `/items/${id}`,
      providesTags: (_result, _err, id) => [{ type: "Items", id }],
    }),

    getPriceHistory: builder.query<PricePoint[], { id: number; days?: number }>({
      query: ({ id, days = 30 }) => `/items/${id}/price-history?days=${days}`,
      providesTags: (_result, _err, { id }) => [{ type: "PriceHistory", id }],
    }),

    submitPrice: builder.mutation<
      PriceSubmission,
      { itemId: number; body: PriceSubmissionCreate }
    >({
      query: ({ itemId, body }) => ({
        url: `/items/${itemId}/submit-price`,
        method: "POST",
        body,
      }),
      invalidatesTags: (_result, _err, { itemId }) => [
        "Items",
        { type: "PriceHistory", id: itemId },
      ],
    }),

    getAlerts: builder.query<PriceAlert[], void>({
      query: () => "/alerts",
      providesTags: ["Alerts"],
    }),

    createAlert: builder.mutation<PriceAlert, PriceAlertCreate>({
      query: (body) => ({
        url: "/alerts",
        method: "POST",
        body,
      }),
      invalidatesTags: ["Alerts"],
    }),

    deleteAlert: builder.mutation<void, number>({
      query: (id) => ({
        url: `/alerts/${id}`,
        method: "DELETE",
      }),
      invalidatesTags: ["Alerts"],
    }),

    seedDatabase: builder.mutation<{ message: string; seeded: boolean }, void>({
      query: () => ({
        url: "/seed",
        method: "POST",
      }),
      invalidatesTags: ["Items", "Alerts"],
    }),
  }),
});

export const {
  useGetCategoriesQuery,
  useGetItemsQuery,
  useGetItemQuery,
  useGetPriceHistoryQuery,
  useSubmitPriceMutation,
  useGetAlertsQuery,
  useCreateAlertMutation,
  useDeleteAlertMutation,
  useSeedDatabaseMutation,
} = groceryApi;
