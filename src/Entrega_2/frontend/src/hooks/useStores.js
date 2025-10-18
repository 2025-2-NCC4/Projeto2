import { useMemo } from "react";
import { useQuery } from "./useQuery";
import { getStores } from "../services/api";

export function useStores(params) {
  const depKey = useMemo(() => JSON.stringify(params || {}), [params]);
  return useQuery(() => getStores(params), [depKey]);
}
