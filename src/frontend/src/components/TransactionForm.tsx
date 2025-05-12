import { Form, Input, InputNumber, Button, Select, DatePicker } from "antd";
import dayjs from "dayjs";

import type { FC } from "react";
import type { TransactionData } from "../types/transaction";

const { Option } = Select;

type Props = {
  onSubmit: (data: TransactionData) => void;
  isLoading?: boolean;
};

export const TransactionForm: FC<Props> = ({ isLoading = false, onSubmit }) => {
  const [form] = Form.useForm();

  const handleFinish = (values: TransactionData) => {
    const data: TransactionData = {
      ...values,
      dob: dayjs(values.dob).format("YYYY-MM-DD"),
    };

    onSubmit(data);
  };

  return (
    <Form
      layout="vertical"
      disabled={isLoading}
      form={form}
      onFinish={handleFinish}
      initialValues={{
        gender: "M",
        category: "misc_net",
        amt: 1.0,
      }}
    >
      <Form.Item
        label="Credit Card Number"
        name="cc_num"
        rules={[{ required: true }]}
      >
        <Input />
      </Form.Item>

      <Form.Item label="Merchant" name="merchant" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Category" name="category" rules={[{ required: true }]}>
        <Select>
          <Option value="misc_net">misc_net</Option>
          <Option value="shopping_pos">shopping_pos</Option>
          <Option value="gas_transport">gas_transport</Option>
        </Select>
      </Form.Item>

      <Form.Item label="Amount" name="amt" rules={[{ required: true }]}>
        <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item label="First Name" name="first" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Last Name" name="last" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Gender" name="gender" rules={[{ required: true }]}>
        <Select>
          <Option value="M">Male</Option>
          <Option value="F">Female</Option>
        </Select>
      </Form.Item>

      <Form.Item label="Street" name="street" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="City" name="city" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="State" name="state" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Zip Code" name="zip" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Latitude" name="lat" rules={[{ required: true }]}>
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item label="Longitude" name="long" rules={[{ required: true }]}>
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item
        label="City Population"
        name="city_pop"
        rules={[{ required: true }]}
      >
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item label="Job" name="job" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Date of Birth" name="dob" rules={[{ required: true }]}>
        <DatePicker style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item
        label="Transaction Number"
        name="trans_num"
        rules={[{ required: true }]}
      >
        <Input />
      </Form.Item>

      <Form.Item
        label="Unix Time"
        name="unix_time"
        rules={[{ required: true }]}
      >
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item
        label="Merchant Latitude"
        name="merch_lat"
        rules={[{ required: true }]}
      >
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item
        label="Merchant Longitude"
        name="merch_long"
        rules={[{ required: true }]}
      >
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" block>
          Submit
        </Button>
      </Form.Item>
    </Form>
  );
};
