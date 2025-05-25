import {
  describe,
  it,
  expect,
  vi,
  beforeEach,
  afterEach,
  type MockedFunction,
} from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useTransactions } from "./useTransactions";
import type { TransactionData } from "../types/transaction";

const mockPayload: TransactionData = {
  cc_num: "1234567890123456",
  merchant: "Starbucks",
  category: "coffee",
  amt: 4.95,
  first: "Alice",
  last: "Smith",
  gender: "F",
  street: "1 Coffee Road",
  city: "Seattle",
  state: "WA",
  zip: "98101",
  lat: 47.6097,
  long: -122.3331,
  city_pop: 1000000,
  job: "Barista",
  dob: "1990-01-01",
  trans_num: "abc123",
  trans_date_trans_time: "2020-06-21 12:14:25",
  unix_time: 1592734465,
  merch_lat: 47.6098,
  merch_long: -122.3332,
};

const mockResponse = {
  prediction: 1,
  is_fraud: true,
  fraud_probability: 0.842,
  transaction_id: "abc123",
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

describe("useTransactions", () => {
  it("initializes with no data or error", () => {
    const { result } = renderHook(() => useTransactions());
    expect(result.current.data).toBeUndefined();
    expect(result.current.error).toBeUndefined();
    expect(result.current.isLoading).toBe(false);
  });

  it("sends request and sets data on success", async () => {
    const { result } = renderHook(() => useTransactions());

    await act(async () => {
      await result.current.submit(mockPayload);
    });

    expect(fetch).toHaveBeenCalledWith(
      "/api/predict",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );

    expect(result.current.data).toEqual(mockResponse);
    expect(result.current.error).toBeUndefined();
    expect(result.current.isLoading).toBe(false);
  });

  it("handles API error response", async () => {
    (fetch as MockedFunction<typeof fetch>).mockImplementationOnce(
      // @ts-expect-error we don't need the whole fetch result
      async () => ({ ok: false, statusText: "Bad Request" }),
    );

    const { result } = renderHook(() => useTransactions());

    await act(async () => {
      await result.current.submit(mockPayload);
    });

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toMatch(/API Error/i);
    expect(result.current.data).toBeUndefined();
    expect(result.current.isLoading).toBe(false);
  });

  it("handles network failure", async () => {
    (fetch as MockedFunction<typeof fetch>).mockImplementationOnce(async () => {
      throw new Error("Network fail");
    });

    const { result } = renderHook(() => useTransactions());

    await act(async () => {
      await result.current.submit(mockPayload);
    });

    expect(result.current.error).toBeInstanceOf(Error);
    expect(result.current.error?.message).toMatch(/Network fail/i);
    expect(result.current.data).toBeUndefined();
  });

  it("resets data with reset()", async () => {
    const { result } = renderHook(() => useTransactions());

    await act(async () => {
      await result.current.submit(mockPayload);
    });

    expect(result.current.data).toEqual(mockResponse);

    act(() => {
      result.current.reset();
    });

    expect(result.current.data).toBeUndefined();
  });
});
