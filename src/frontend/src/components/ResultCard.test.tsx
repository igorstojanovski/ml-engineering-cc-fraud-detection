import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ResultCard } from "./ResultCard";

describe("ResultCard", () => {
  const baseResult = {
    prediction: 1,
    is_fraud: true,
    fraud_probability: 0.832,
    transaction_id: "abc123",
  };

  it("renders fraud result with red tag", () => {
    render(<ResultCard result={baseResult} onReset={vi.fn()} />);
    expect(screen.getByText("Fraudulent")).toBeInTheDocument();
    expect(screen.getByText("0.832")).toBeInTheDocument();
    expect(screen.getByText("abc123")).toBeInTheDocument();
  });

  it("renders legitimate result with green tag", () => {
    render(
      <ResultCard
        result={{ ...baseResult, is_fraud: false, prediction: 0 }}
        onReset={vi.fn()}
      />,
    );
    expect(screen.getByText("Legitimate")).toBeInTheDocument();
  });
});
