import { Typography, Tag, Modal } from "antd";
import type { TransactionResponse } from "../types/transaction";

const { Title, Paragraph, Text } = Typography;

interface ResultCardProps {
  result: TransactionResponse | void;
  onReset: () => void;
}

export const ResultCard = ({ result, onReset }: ResultCardProps) => (
  <Modal
    open={!!result}
    onCancel={onReset}
    footer={null}
    title="Prediction Result"
    destroyOnClose
  >
    {result ? (
      <div style={{ paddingTop: 8 }}>
        <Title level={4}>
          {result.is_fraud ? (
            <Tag color="red">Fraudulent</Tag>
          ) : (
            <Tag color="green">Legitimate</Tag>
          )}
        </Title>

        <Paragraph>
          <Text strong>Fraud Probability:</Text>{" "}
          {result.fraud_probability.toFixed(3)}
        </Paragraph>

        <Paragraph>
          <Text strong>Prediction Code:</Text> {result.prediction}
        </Paragraph>

        <Paragraph>
          <Text strong>Transaction ID:</Text> {result.transaction_id}
        </Paragraph>
      </div>
    ) : null}
  </Modal>
);
