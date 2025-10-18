import http from "./http";

export const getPlayers = (params) =>
  http.get("api/players", { params }).then((r) => r.data);

export const getTransactions = (params) =>
  http.get("api/transactions", { params }).then((r) => r.data);

export const getStores = (params) =>
  http.get("api/stores", { params }).then((r) => r.data);

export const getSimulations = (params) =>
  http.get("api/simulations", { params }).then((r) => r.data);

export const getTable = (endpoint, params) =>
  http.get(endpoint, { params }).then((r) => r.data);
