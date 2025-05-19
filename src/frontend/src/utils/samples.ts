import dayjs from "dayjs";
import type { TransactionFormData } from "../types/transaction.ts";

export const sample1: TransactionFormData = {
  trans_date_trans_time: dayjs("2020-06-21 12:14:25"),
  first: "Alice",
  last: "Williams",
  gender: "F",
  dob: dayjs("1992-07-14"),
  job: "Software Engineer",
  merchant: "Best Buy",
  category: "electronics",
  amt: 249.99,
  trans_num: "abc123-sample-1",
  unix_time: 1592741665,

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
  trans_date_trans_time: dayjs("2020-12-01 08:45:10"),
  first: "Bob",
  last: "Anderson",
  gender: "M",
  dob: dayjs("1985-03-22"),
  job: "Data Analyst",
  merchant: "Target",
  category: "groceries",
  amt: 42.95,
  trans_num: "xyz789-sample-2",
  unix_time: 1606812310,

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

export const fraudSample: TransactionFormData = {
  trans_date_trans_time: dayjs("2020-06-21 12:14:33"),
  cc_num: "3573030041201292",
  merchant: "fraud_Sporer-Keebler",
  category: "personal_care",
  amt: 29.84,
  first: "Joanne",
  last: "Williams",
  gender: "F",
  street: "3638 Marsh Union",
  city: "Altonah",
  state: "UT",
  zip: "84002",
  lat: 40.3207,
  long: -110.436,
  city_pop: 302,
  job: "Sales professional, IT",
  dob: dayjs("1990-01-17"),
  trans_num: "324cc204407e99f51b0d6ca0055005e7",
  unix_time: 1371816873,
  merch_lat: 39.450498,
  merch_long: -109.960431,
};
