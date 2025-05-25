import type {
  TransactionData,
  TransactionFormData,
} from "../types/transaction";
import dayjs from "dayjs";

const ORDERED_FEATURES = [
  "trans_date_trans_time",
  "cc_num",
  "merchant",
  "category",
  "amt",
  "first",
  "last",
  "gender",
  "street",
  "city",
  "state",
  "zip",
  "lat",
  "long",
  "city_pop",
  "job",
  "dob",
  "trans_num",
  "unix_time",
  "merch_lat",
  "merch_long",
] as const satisfies Readonly<(keyof TransactionData)[]>;

export function createOrderedTransaction<T extends TransactionData>(
  values: Partial<T>,
): T {
  const ordered: Partial<Record<keyof T, T[keyof T]>> = {};

  for (const key of ORDERED_FEATURES) {
    ordered[key] = values[key]!;
  }

  return ordered as T;
}

export function normalizeTransactionFormData(
  values: TransactionFormData,
): TransactionData {
  return {
    ...values,
    dob: dayjs(values.dob).format("YYYY-MM-DD"),
    trans_date_trans_time: dayjs(values.trans_date_trans_time).format(
      "YYYY-MM-DD HH:mm:ss",
    ),
    unix_time: dayjs(values.trans_date_trans_time).unix(),
  };
}
