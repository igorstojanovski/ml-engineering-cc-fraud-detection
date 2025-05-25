import {
  describe,
  it,
  expect,
  vi,
  beforeEach,
  type MockedFunction,
} from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MerchantAutocomplete } from "./MerchantAutocomplete";
import { useGeocoding } from "../hooks/useGeocoding";
import { Form } from "antd";

vi.mock("../hooks/useGeocoding");

const mockSuggestion = {
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
};

describe("MerchantAutocomplete", () => {
  beforeEach(() => {
    (useGeocoding as MockedFunction<typeof useGeocoding>).mockImplementation(
      () => ({
        error: null,
        loading: false,
        search: vi.fn(),
        results: [mockSuggestion],
      }),
    );
  });

  it("renders input field", () => {
    render(
      <Form>
        <MerchantAutocomplete onSelect={vi.fn()} />
      </Form>,
    );
    expect(screen.getByText("Enter merchant name")).toBeInTheDocument();
  });

  it("calls onSelect with parsed address from suggestion", async () => {
    const onSelect = vi.fn();

    render(
      <Form>
        <MerchantAutocomplete onSelect={onSelect} />
      </Form>,
    );

    const input = screen.getByRole("combobox");
    await userEvent.type(input, "221B");

    const content = document.querySelector(".ant-select-item-option-content");

    expect(content).toBeInTheDocument();
    expect(content).toHaveTextContent("221B Baker Street");

    await userEvent.click(content!);

    expect(onSelect).toHaveBeenCalledWith(mockSuggestion);
  });
});
