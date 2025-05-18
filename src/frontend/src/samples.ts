import dayjs from "dayjs";
import type { TransactionFormData } from "./types/transaction.ts";

export const sample1: TransactionFormData = {
  first: "Alice",
  last: "Williams",
  gender: "F",
  dob: dayjs("1992-07-14"),
  job: "Software Engineer",
  merchant: "Best Buy",
  category: "electronics",
  amt: 249.99,
  trans_num: "abc123-sample-1",
  unix_time: 1650912000,

  street: "123 Broadway",
  city: "New York",
  state: "NY",
  zip: "10001",
  lat: 40.7128,
  long: -74.006,
  city_pop: 8500000,

  merch_lat: 40.7505,
  merch_long: -73.9934,
  cc_num: "1234567890123456",
};

export const sample2: TransactionFormData = {
  first: "Bob",
  last: "Anderson",
  gender: "M",
  dob: dayjs("1985-03-22"),
  job: "Data Analyst",
  merchant: "Target",
  category: "groceries",
  amt: 42.95,
  trans_num: "xyz789-sample-2",
  unix_time: 1650998400,

  street: "456 Elm St",
  city: "San Francisco",
  state: "CA",
  zip: "94107",
  lat: 37.7749,
  long: -122.4194,
  city_pop: 870000,

  merch_lat: 37.7792,
  merch_long: -122.4173,
  cc_num: "9876543210987654",
};
