import React from "react";
import { SearchOutlined } from "@ant-design/icons";

const PageNotFound = () => {
  return (
    <div className="error-page">
        <SearchOutlined />
      <h1>
        Page not found
      </h1>
      <p>The page you are looking for could not be found.</p>
    </div>
  );
};

export default PageNotFound;
