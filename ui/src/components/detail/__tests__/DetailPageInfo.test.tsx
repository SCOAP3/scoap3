import React from "react";
import { render, screen } from "@testing-library/react";

import DetailPageInfo from "../DetailPageInfo";
import { record } from '@/mocks/record';

describe("DetailPageInfo", () => {
  it("renders detail page info correctly", () => {
    const { container } = render(<DetailPageInfo article={record} />);

    expect(container).toMatchSnapshot();
    expect(screen.getByText("Published on:")).toBeInTheDocument();
    expect(screen.getByText("25 June 2015")).toBeInTheDocument();
    expect(screen.getByText("Created on:")).toBeInTheDocument();
    expect(screen.getByText("30 April 2018")).toBeInTheDocument();
    expect(screen.getByText("Springer/SISSA")).toBeInTheDocument();
    expect(screen.getByText("Published in:")).toBeInTheDocument();
    expect(screen.getByText("Journal of High Energy Physics")).toBeInTheDocument();
    expect(screen.getByText("(2015)")).toBeInTheDocument();
    expect(screen.getByText("Pages 171-189")).toBeInTheDocument();
    expect(screen.getByText("DOI:")).toBeInTheDocument();
    expect(screen.getByText("10.1007/JHEP06(2015)171")).toBeInTheDocument();
    expect(screen.getByText("arXiv:")).toBeInTheDocument();
    expect(screen.getByText("hep-th")).toBeInTheDocument();
    expect(screen.getByText("1504.07579")).toBeInTheDocument();
    expect(screen.getByText("Copyrights:")).toBeInTheDocument();
    expect(screen.getByText("The Author(s)")).toBeInTheDocument();
    expect(screen.getByText("Licence:")).toBeInTheDocument();
    expect(screen.getByText("CC-BY-4.0")).toBeInTheDocument();
    expect(screen.getByText("Fulltext files:")).toBeInTheDocument();
    expect(screen.getByText("XML")).toBeInTheDocument();
    expect(screen.getByText("PDF/A")).toBeInTheDocument();
  });
});
