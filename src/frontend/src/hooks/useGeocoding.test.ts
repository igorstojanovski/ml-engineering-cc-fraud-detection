import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useGeocoding } from "./useGeocoding";

const mockResponse = {
  results: [
    {
      formatted: "221B Baker Street, London, NW1 6XE, United Kingdom",
      geometry: {
        lat: 51.523767,
        lng: -0.1585557,
      },
      components: {
        road: "Baker Street",
        city: "London",
        state: "England",
        postcode: "NW1 6XE",
        country: "United Kingdom",
        suburb: "Marylebone",
        neighbourhood: "Regent’s Park",
      },
    },
  ],
};

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      }),
    ),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useGeocoding", () => {
  it("initializes with default state", () => {
    const { result } = renderHook(() => useGeocoding());
    expect(result.current.results).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it("does not search for short query", async () => {
    const { result } = renderHook(() => useGeocoding());

    await act(async () => {
      await result.current.search("ab"); // < 3 символов
    });

    expect(fetch).not.toHaveBeenCalled();
    expect(result.current.results).toEqual([]);
  });

  it("fetches and stores results on valid search", async () => {
    const { result } = renderHook(() => useGeocoding());

    await act(async () => {
      await result.current.search("221B Baker Street");
    });

    expect(fetch).toHaveBeenCalled();
    expect(result.current.results).toHaveLength(1);
    expect(result.current.results[0].formatted).toMatch(/Baker Street/);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("handles fetch failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("Network Error"))),
    );

    const { result } = renderHook(() => useGeocoding());

    await act(async () => {
      await result.current.search("fail address");
    });

    expect(result.current.results).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toBe("Network Error");
  });
});
