import React from "react";
import { render, screen } from "@testing-library/react";
import { MathJaxContext } from "better-react-mathjax";

import ResultItem from "../ResultItem";
import { record } from "@/mocks/index";

describe("ResultItem", () => {
  it("renders result item correctly", () => {
    render(
      <MathJaxContext>
        <ResultItem article={record} />
      </MathJaxContext>
    );

    expect(
      screen.getByText(
        "Strings from 3D gravity: asymptotic dynamics of AdS 3 gravity with free boundary conditions"
      )
    ).toBeInTheDocument();
    expect(screen.getByText("Apolo, Luis")).toBeInTheDocument();
    expect(
      screen.getByText("Journal of High Energy Physics")
    ).toBeInTheDocument();
    expect(screen.getByText("10.1007/JHEP06(2015)171")).toBeInTheDocument();
    expect(screen.getByText("XML")).toBeInTheDocument();
    expect(screen.getByText("PDF/A")).toBeInTheDocument();
  });

  it("renders link to the record page correctly", () => {
    render(
      <MathJaxContext>
        <ResultItem article={record} />
      </MathJaxContext>
    );

    const link = screen.getByRole("link", {
      name: /Strings from 3D gravity: asymptotic dynamics of AdS 3 gravity with free boundary conditions/i,
    });
    expect(link).toHaveAttribute("href", "/records/10913");
  });
});
