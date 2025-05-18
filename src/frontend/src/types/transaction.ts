import type { Dayjs } from "dayjs";

export interface TransactionBaseData {
  cc_num: string;
  merchant: string;
  category: string;
  amt: number;
  first: string;
  last: string;
  gender: string;
  street: string;
  city: string;
  state: string;
  zip: string;
  lat: number;
  long: number;
  city_pop: number;
  job: string;
  dob: string | Dayjs; // ISO 8601
  trans_num: string;
  unix_time: number;
  merch_lat: number;
  merch_long: number;
}

export interface TransactionData extends TransactionBaseData {
  dob: string;
}

export interface TransactionFormData extends TransactionBaseData {
  dob: Dayjs;
}

export interface TransactionResponse {
  prediction: number;
  is_fraud: boolean;
  fraud_probability: number;
  transaction_id: string;
}
