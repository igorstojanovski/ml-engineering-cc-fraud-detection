import { Button, Col, Row } from "antd";
import type { TransactionFormData } from "../types/transaction.ts";
import { sample1, sample2 } from "../utils/samples.ts";

interface SampleButtonsProps {
  onSubmit: (data: TransactionFormData) => void;
}

export const SampleButtons = ({ onSubmit }: SampleButtonsProps) => (
  <Row gutter={8} style={{ marginBottom: 24 }}>
    <Col>
      <Button onClick={() => onSubmit(sample1)}>Sample Data 1</Button>
    </Col>
    <Col>
      <Button onClick={() => onSubmit(sample2)}>Sample Data 2</Button>
    </Col>
  </Row>
);
