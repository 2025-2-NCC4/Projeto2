import { useEffect, useMemo, useRef, useState } from "react";

export function useQuery(queryFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const refetchTick = useRef(0);

  const stableDeps = useMemo(() => deps, deps);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await queryFn();
      setData(res);
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Falha ao carregar dados"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await queryFn();
        if (alive) setData(res);
      } catch (e) {
        if (alive) setError(e instanceof Error ? e : new Error("Falha ao carregar dados"));
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [refetchTick.current, ...stableDeps]);

  const refetch = () => {
    refetchTick.current += 1;
  };

  return { data, loading, error, refetch };
}
