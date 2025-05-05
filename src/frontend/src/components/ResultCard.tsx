// src/components/Result.tsx
import { Card, Typography, Tag } from "antd";
import type { TransactionResponse } from "../types/transaction";

const { Title, Paragraph, Text } = Typography;

interface ResultCardProps {
  result: TransactionResponse | void;
}

export const ResultCard = ({ result }: ResultCardProps) => {
  if (!result) return null;

  return (
    <Card title="Prediction Result" style={{ marginTop: 24 }}>
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
    </Card>
  );
};
