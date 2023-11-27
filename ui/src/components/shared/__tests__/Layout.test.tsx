import React from "react";
import { render } from "@testing-library/react";

import Layout from "../Layout";

describe("Layout", () => {
  it("renders layout component correctly", () => {
    const { container } = render(
      <Layout>
        <div>Hi</div>
      </Layout>
    );

    expect(container).toMatchSnapshot();
  });
});
