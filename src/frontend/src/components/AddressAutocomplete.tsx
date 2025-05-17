import { AutoComplete, Input, Spin } from "antd";
import { useEffect, useMemo, useState } from "react";
import { type OpenCageResult, useGeocoding } from "../hooks/useGeocoding";
import debounce from "lodash.debounce";

type AddressAutocompleteProps = {
  value?: string;
  onChange?: (value: string) => void;
  onSelect: (result: OpenCageResult) => void;
  placeholder?: string;
};

export const AddressAutocomplete = ({
  value,
  onChange,
  onSelect,
  placeholder,
}: AddressAutocompleteProps) => {
  const { results, loading, search } = useGeocoding();
  const [input, setInput] = useState("");

  const debouncedSearch = useMemo(() => debounce(search, 400), [search]);

  useEffect(() => {
    debouncedSearch(input);
    return () => debouncedSearch.cancel();
  }, [input, debouncedSearch]);

  const options = results.map((r) => ({
    value: r.formatted,
    label: r.formatted,
    meta: r,
  }));

  const handleSelect = (value: string, option: { meta: OpenCageResult }) => {
    onSelect(option.meta);
    onChange?.(value);
  };

  return (
    <AutoComplete
      value={value}
      style={{ width: "100%" }}
      options={options}
      onSelect={handleSelect}
      onSearch={setInput}
      placeholder={placeholder ?? "Enter address"}
    >
      <Input suffix={loading ? <Spin size="small" /> : null} />
    </AutoComplete>
  );
};
