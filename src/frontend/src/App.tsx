import { useEffect } from "react";
import { App as AntdApp, Layout, Typography } from "antd";
import { TransactionForm } from "./components/TransactionForm";
import { ResultCard } from "./components/ResultCard";
import { useTransaction } from "./hooks/useTransactions.tsx";

function App() {
  const { error, isLoading, data, submit } = useTransaction();
  const { message } = AntdApp.useApp();

  useEffect(() => {
    error && message.error(error.message);
  }, [error]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header style={{ color: "#fff", fontSize: 18 }}>
        ML Inference UI
      </Layout.Header>
      <Layout.Content style={{ padding: "20px 48px" }}>
        <Typography.Title level={3}>Enter data for prediction</Typography.Title>
        <TransactionForm isLoading={isLoading} onSubmit={submit} />
        <ResultCard result={data} />
      </Layout.Content>
    </Layout>
  );
}

export default App;
