import { configureStore, combineReducers, createSlice } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { groceryApi } from "./api";

const appSlice = createSlice({
  name: "app",
  initialState: { initialized: true },
  reducers: {},
});

const persistConfig = {
  key: "root",
  storage: AsyncStorage,
  blacklist: [groceryApi.reducerPath],
};

const rootReducer = combineReducers({
  app: appSlice.reducer,
  [groceryApi.reducerPath]: groceryApi.reducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ["persist/PERSIST", "persist/REHYDRATE"],
      },
    }).concat(groceryApi.middleware),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
