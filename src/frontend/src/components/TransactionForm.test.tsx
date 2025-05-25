import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TransactionForm } from "./TransactionForm";

describe("TransactionForm", () => {
  it("renders the required fields", () => {
    render(<TransactionForm onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Predict/i }),
    ).toBeInTheDocument();
  });

  it("shows validation error when submitting empty form", async () => {
    render(<TransactionForm onSubmit={vi.fn()} />);

    await userEvent.click(screen.getByRole("button", { name: /Predict/i }));

    await waitFor(() => {
      expect(screen.getAllByText(/required/i).length).toBeGreaterThan(0);
    });
  });
});
