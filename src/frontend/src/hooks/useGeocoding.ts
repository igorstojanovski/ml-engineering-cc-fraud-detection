import { useState, useCallback } from "react";

const OPENCAGE_TOKEN = import.meta.env.VITE_OPENCAGE_TOKEN;
const ENDPOINT = "https://api.opencagedata.com/geocode/v1/json";

export type OpenCageResult = {
  formatted: string;
  geometry: {
    lat: number;
    lng: number;
  };
  components: {
    road?: string;
    city?: string;
    town?: string;
    village?: string;
    state?: string;
    shop?: string;
    suburb?: string;
    postcode?: string;
    country?: string;
    neighbourhood?: string;
    office?: string;
  };
};

export const useGeocoding = () => {
  const [results, setResults] = useState<OpenCageResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const search = useCallback(async (query: string) => {
    if (!query || query.length < 3) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const url = `${ENDPOINT}?q=${encodeURIComponent(query)}&key=${OPENCAGE_TOKEN}&language=en`;
      const res = await fetch(url);
      const json = await res.json();
      setResults(json.results ?? []);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, []);

  return { results, loading, error, search };
};
