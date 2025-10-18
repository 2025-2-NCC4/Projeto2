
import React, { useMemo } from "react";
import { useTransactions } from "../hooks/useTransactions";


export default function Dashboard() {
  const { data: tx, loading, error, refetch } = useTransactions({ year: 2025 });

  const total = useMemo(() => (tx ? tx.reduce((acc, t) => acc + (t.valor || 0), 0) : 0), [tx]);

  if (loading) return <p>Carregando…</p>;
  if (error) return <p>Erro: {error.message}</p>;

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Total {total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</p>
      <button onClick={refetch}>Atualizar</button>
      <pre>{JSON.stringify(tx?.slice(0, 5), null, 2)}...</pre>
    </div>
  );
}
