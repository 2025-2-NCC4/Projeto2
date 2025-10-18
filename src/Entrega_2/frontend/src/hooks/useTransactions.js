import { useMemo } from "react";
import { useQuery } from "./useQuery";
import { getTransactions } from "../services/api";

export function useTransactions(params) {
  const depKey = useMemo(() => JSON.stringify(params || {}), [params]);
  return useQuery(() => getTransactions(params), [depKey]);
}
