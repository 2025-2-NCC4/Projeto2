import { useMemo } from "react";
import { useQuery } from "./useQuery";
import { getPlayers } from "../services/api";

export function usePlayers(params) {
  const depKey = useMemo(() => JSON.stringify(params || {}), [params]);
  return useQuery(() => getPlayers(params), [depKey]);
}
