import { Button, Col, Row } from "antd";
import type { TransactionFormData } from "../types/transaction";
import { fraudSample1, sample1 } from "../utils/samples";

interface SampleButtonsProps {
  onSubmit: (data: TransactionFormData) => void;
}

export const SampleButtons = ({ onSubmit }: SampleButtonsProps) => (
  <Row gutter={8} style={{ marginBottom: 24 }}>
    <Col>
      <Button onClick={() => onSubmit(sample1)}>Legit Sample 1</Button>
    </Col>
    <Col>
      <Button onClick={() => onSubmit(fraudSample1)}>Fraud Sample 1</Button>
    </Col>
  </Row>
);
