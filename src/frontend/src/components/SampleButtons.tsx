import { Button, Col, Row } from "antd";
import type { TransactionFormData } from "../types/transaction";
import { fraudSample, sample1, sample2 } from "../utils/samples";

interface SampleButtonsProps {
  onSubmit: (data: TransactionFormData) => void;
}

export const SampleButtons = ({ onSubmit }: SampleButtonsProps) => (
  <Row gutter={8} style={{ marginBottom: 24 }}>
    <Col>
      <Button onClick={() => onSubmit(sample1)}>Legit Sample 1</Button>
    </Col>
    <Col>
      <Button onClick={() => onSubmit(sample2)}>Legit Sample 2</Button>
    </Col>
    <Col>
      <Button onClick={() => onSubmit(fraudSample)}>Fraud Sample 1</Button>
    </Col>
  </Row>
);
