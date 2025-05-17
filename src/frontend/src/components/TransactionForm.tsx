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
  Collapse,
} from "antd";
import dayjs from "dayjs";
import type {
  TransactionData,
  TransactionFormData,
} from "../types/transaction";
import { AddressAutocomplete } from "./AddressAutocomplete.tsx";
import type { OpenCageResult } from "../hooks/useGeocoding.ts";
import { MerchantAutocomplete } from "./MerchantAutocomplete.tsx";
import { SampleButtons } from "./SampleButtons.tsx";

type TransactionFormProps = {
  onSubmit: (data: TransactionData) => void;
  isLoading?: boolean;
};

const genderOptions = [
  { value: "F", label: "Female" },
  { value: "M", label: "Male" },
];

export const TransactionForm = ({
  isLoading = false,
  onSubmit,
}: TransactionFormProps) => {
  const [form] = Form.useForm<TransactionFormData>();

  const handleFinish = (values: TransactionFormData) => {
    onSubmit({
      ...values,
      dob: dayjs(values.dob).format("YYYY-MM-DD"),
    });
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
      components: { neighbourhood, office },
    } = result;
    const values = {
      merch_lat: lat,
      merch_long: lng,
      merchant: office ?? neighbourhood,
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
      <Form.Item>
        <Collapse size="small">
          <Collapse.Panel key="location" header="Advanced location data">
            <Form.Item
              name="street"
              label="Street"
              rules={[{ required: true }]}
            >
              <Input />
            </Form.Item>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="city"
                  label="City"
                  rules={[{ required: true }]}
                >
                  <Input />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  name="state"
                  label="State"
                  rules={[{ required: true }]}
                >
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
                <Form.Item
                  name="lat"
                  label="Latitude"
                  rules={[{ required: true }]}
                >
                  <InputNumber style={{ width: "100%" }} />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  name="long"
                  label="Longitude"
                  rules={[{ required: true }]}
                >
                  <InputNumber style={{ width: "100%" }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item name="city_pop" label="City Population">
                  <InputNumber style={{ width: "100%" }} />
                </Form.Item>
              </Col>
            </Row>
          </Collapse.Panel>
        </Collapse>
      </Form.Item>

      <Divider orientation="left">🏬 Merchant</Divider>
      <Form.Item label="Search">
        <MerchantAutocomplete onSelect={handleMerchantSelect} />
      </Form.Item>
      <Form.Item>
        <Collapse size="small">
          <Collapse.Panel key="location" header="Advanced location data">
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
          </Collapse.Panel>
        </Collapse>
      </Form.Item>
      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true }]}
          >
            <Input />
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
        name="unix_time"
        label="Timestamp (Unix)"
        rules={[{ required: true }]}
      >
        <InputNumber style={{ width: "100%" }} />
      </Form.Item>

      <Form.Item>
        <Button loading={isLoading} type="primary" htmlType="submit">
          Predict
        </Button>
      </Form.Item>
    </Form>
  );
};
