import { AutoComplete, Input, Spin } from "antd";
import { useEffect, useMemo, useState } from "react";
import { useGeocoding, type OpenCageResult } from "../hooks/useGeocoding.ts";
import debounce from "lodash.debounce";

type MerchantAutocompleteProps = {
  value?: string;
  onChange?: (value: string) => void;
  onSelect?: (result: OpenCageResult | null) => void;
  placeholder?: string;
};

export const MerchantAutocomplete = ({
  value,
  onChange,
  onSelect,
  placeholder,
}: MerchantAutocompleteProps) => {
  const { results, loading, search } = useGeocoding();
  const [input, setInput] = useState(value ?? "");

  const debouncedSearch = useMemo(() => debounce(search, 400), [search]);

  useEffect(() => {
    if (input) debouncedSearch(input);
    return () => debouncedSearch.cancel();
  }, [input, debouncedSearch]);

  const options = results.map((r) => ({
    value: r.formatted,
    label: r.formatted,
    meta: r,
  }));

  const handleSelect = (_: string, option: any) => {
    const result = option.meta as OpenCageResult;
    onChange?.(result.formatted);
    onSelect?.(result);
  };
  const handleChange = (value: string) => {
    setInput(value);
    onChange?.(value);
    onSelect?.(null); // coord reset, if changed manually
  };

  return (
    <AutoComplete
      value={input}
      onChange={handleChange}
      onSelect={handleSelect}
      options={options}
      placeholder={placeholder ?? "Enter merchant name"}
      style={{ width: "100%" }}
    >
      <Input suffix={loading ? <Spin size="small" /> : null} />
    </AutoComplete>
  );
};
