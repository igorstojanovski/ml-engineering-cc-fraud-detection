import { useState } from "react";
import type {
  TransactionData,
  TransactionResponse,
} from "../types/transaction";

export function useTransactions() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<void | Error>(undefined);
  const [data, setData] = useState<void | TransactionResponse>(undefined);

  const reset = () => setData(undefined);
  const submit = async (payload: TransactionData) => {
    setIsLoading(true);
    setError(undefined);

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transaction_data: payload }),
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.statusText}`);
      }

      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err as Error);
      setData(undefined);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    data,
    submit,
    reset,
  };
}
