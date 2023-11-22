import React from "react";
import { useRouter } from "next/router";
import { ExclamationCircleOutlined } from "@ant-design/icons";

const ServerErrorPage = () => {
  const router = useRouter();

  return (
    <div className="error-page">
      <ExclamationCircleOutlined />
      <h1>Something went wrong</h1>
      <p>
        Please try again later or{" "}
        <a type="button" onClick={() => router.push('/')}>
          go to home page
        </a>
      </p>
    </div>
  );
};

export default ServerErrorPage;
