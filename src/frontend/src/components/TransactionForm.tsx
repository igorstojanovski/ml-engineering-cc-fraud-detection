import {
  Form,
  Input,
  InputNumber,
  Button,
  Select,
  DatePicker,
  Divider,
  Col,
  Row,
} from "antd";
import type {
  TransactionData,
  TransactionFormData,
} from "../types/transaction";
import { AddressAutocomplete } from "./AddressAutocomplete";
import type { OpenCageResult } from "../hooks/useGeocoding";
import { MerchantAutocomplete } from "./MerchantAutocomplete";
import { SampleButtons } from "./SampleButtons";
import {
  createOrderedTransaction,
  normalizeTransactionFormData,
} from "../utils/orderTransaction";

type TransactionFormProps = {
  onSubmit: (data: TransactionData) => void;
  isLoading?: boolean;
};

const genderOptions = [
  { value: "F", label: "Female" },
  { value: "M", label: "Male" },
];

const categoryOptions = [
  { value: "entertainment", label: "Entertainment" },
  { value: "food_dining", label: "Food Dining" },
  { value: "gas_transport", label: "Gas Transport" },
  { value: "grocery_net", label: "Grocery Net" },
  { value: "grocery_pos", label: "Grocery Pos" },
  { value: "health_fitness", label: "Health Fitness" },
  { value: "home", label: "Home" },
  { value: "kids_pets", label: "Kids Pets" },
  { value: "misc_net", label: "Misc Net" },
  { value: "misc_pos", label: "Misc Pos" },
  { value: "personal_care", label: "Personal Care" },
  { value: "shopping_net", label: "Shopping Net" },
  { value: "shopping_pos", label: "Shopping Pos" },
  { value: "travel", label: "Travel" },
];

export const TransactionForm = ({
  isLoading = false,
  onSubmit,
}: TransactionFormProps) => {
  const [form] = Form.useForm<TransactionFormData>();

  const handleFinish = (values: TransactionFormData) => {
    const data = normalizeTransactionFormData(values);

    onSubmit(createOrderedTransaction(data));
  };
  const handleAddressSelect = (result: OpenCageResult) => {
    const {
      geometry: { lng, lat },
      components: { postcode, state, city, town, village, road, suburb },
    } = result;
    const values = {
      lat,
      long: lng,
      state: state ?? suburb,
      zip: postcode,
      city: city ?? town ?? village,
      street: road,
    };

    form.setFieldsValue(values);
  };
  const handleMerchantSelect = (result: OpenCageResult | null) => {
    if (!result) return;

    const {
      geometry: { lat, lng },
      components: { neighbourhood, office, shop },
    } = result;
    const values = {
      merch_lat: lat,
      merch_long: lng,
      merchant: office ?? neighbourhood ?? shop,
    };
    form.setFieldsValue(values);
  };

  return (
    <Form<TransactionFormData>
      layout="vertical"
      disabled={isLoading}
      form={form}
      onFinish={handleFinish}
      initialValues={{
        gender: "M",
        category: "misc_net",
        amt: 1.0,
        city_pop: 1000,
      }}
    >
      <SampleButtons onSubmit={(data) => form.setFieldsValue(data)} />
      <Divider orientation="left">👤 Personal Information</Divider>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="first"
            label="First Name"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="last" label="Last Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="gender" label="Gender" rules={[{ required: true }]}>
            <Select options={genderOptions} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="dob"
            label="Date of Birth"
            rules={[{ required: true }]}
          >
            <DatePicker style={{ width: "100%" }} />
          </Form.Item>
        </Col>
      </Row>
      <Form.Item name="job" label="Occupation" rules={[{ required: true }]}>
        <Input />
      </Form.Item>

      <Divider orientation="left">🏠 Address</Divider>
      <Form.Item label="Search">
        <AddressAutocomplete onSelect={handleAddressSelect} />
      </Form.Item>

      <Form.Item name="street" label="Street" rules={[{ required: true }]}>
        <Input />
      </Form.Item>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item name="city" label="City" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="state" label="State" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="zip" label="ZIP" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
        </Col>
      </Row>
      <Row gutter={16}>
        <Col span={6}>
          <Form.Item name="lat" label="Latitude" rules={[{ required: true }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Col>
        <Col span={6}>
          <Form.Item name="long" label="Longitude" rules={[{ required: true }]}>
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="city_pop" label="City Population">
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Col>
      </Row>

      <Divider orientation="left">🏬 Merchant</Divider>
      <Form.Item label="Search">
        <MerchantAutocomplete onSelect={handleMerchantSelect} />
      </Form.Item>

      <Form.Item
        name="merchant"
        label="Merchant Name"
        rules={[{ required: true }]}
      >
        <Input />
      </Form.Item>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="merch_lat"
            label="Merchant Latitude"
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="merch_long"
            label="Merchant Longitude"
            rules={[{ required: true }]}
          >
            <InputNumber style={{ width: "100%" }} />
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true }]}
          >
            <Select options={categoryOptions} />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item name="amt" label="Amount ($)" rules={[{ required: true }]}>
            <InputNumber min={0} step={0.01} style={{ width: "100%" }} />
          </Form.Item>
        </Col>
      </Row>

      <Divider orientation="left">💳 Transaction</Divider>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="cc_num"
            label="Credit Card #"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="trans_num"
            label="Transaction ID"
            rules={[{ required: true }]}
          >
            <Input />
          </Form.Item>
        </Col>
      </Row>
      <Form.Item
        name="trans_date_trans_time"
        label="Transaction Date & Time"
        rules={[{ required: true }]}
      >
        <DatePicker
          showTime
          format="YYYY-MM-DD HH:mm:ss"
          style={{ width: "100%" }}
        />
      </Form.Item>

      <Form.Item>
        <Button loading={isLoading} type="primary" htmlType="submit">
          Predict
        </Button>
      </Form.Item>
    </Form>
  );
};
