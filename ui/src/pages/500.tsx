import React from "react";
import { useRouter } from "next/navigation";
import { ExclamationCircleOutlined } from "@ant-design/icons";

const ServerErrorPage = () => {
  const router = useRouter();

  return (
    <div className="error-page">
      <ExclamationCircleOutlined />
      <h1>Something went wrong</h1>
      <p>
        Please try again later or{" "}
        <a type="button" data-testid="go-back" onClick={() => router.push('/')}>
          go to home page
        </a>
      </p>
    </div>
  );
};

export default ServerErrorPage;
