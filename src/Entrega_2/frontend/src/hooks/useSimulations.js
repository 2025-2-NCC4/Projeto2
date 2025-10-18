import { useMemo } from "react";
import { useQuery } from "./useQuery";
import { getSimulations } from "../services/api";

export function useSimulations(params) {
  const depKey = useMemo(() => JSON.stringify(params || {}), [params]);
  return useQuery(() => getSimulations(params), [depKey]);
}
