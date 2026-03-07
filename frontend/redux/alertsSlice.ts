import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface AlertsState {
  dismissedIds: number[];
}

const initialState: AlertsState = {
  dismissedIds: [],
};

const alertsSlice = createSlice({
  name: "alerts",
  initialState,
  reducers: {
    dismissAlert(state, action: PayloadAction<number>) {
      if (!state.dismissedIds.includes(action.payload)) {
        state.dismissedIds.push(action.payload);
      }
    },
    clearDismissed(state) {
      state.dismissedIds = [];
    },
  },
});

export const { dismissAlert, clearDismissed } = alertsSlice.actions;
export default alertsSlice.reducer;
