import React from "react";
import { render, screen } from "@testing-library/react";
import FulltextFiles from "../FulltextFiles";

const mockFiles = [
  { file: "file1.pdf" },
  { file: "file2.xml" },
  { file: "file3_a.pdf" },
  { file: "file4.txt" }, // Unsupported extension
];

describe("FulltextFiles", () => {
  it("renders supported file formats correctly", () => {
    render(<FulltextFiles files={mockFiles} size="big" />);

    expect(screen.getByText("PDF")).toBeInTheDocument();
    expect(screen.getByText("XML")).toBeInTheDocument();
    expect(screen.getByText("PDF/A")).toBeInTheDocument();

    expect(screen.queryByText("TXT")).toBeNull();
  });

  it("renders file links with correct attributes", () => {
    render(<FulltextFiles files={mockFiles} size="big" />);

    const pdfLink = screen.getByText("PDF");
    expect(pdfLink).toHaveAttribute("href", "file1.pdf");
    expect(pdfLink).toHaveAttribute("download");
    expect(pdfLink).toHaveAttribute("target", "_blank");

    const xmlLink = screen.getByText("XML");
    expect(xmlLink).toHaveAttribute("href", "file2.xml");
    expect(xmlLink).toHaveAttribute("download");
    expect(xmlLink).toHaveAttribute("target", "_blank");

    const pdfaLink = screen.getByText("PDF/A");
    expect(pdfaLink).toHaveAttribute("href", "file3_a.pdf");
    expect(pdfaLink).toHaveAttribute("download");
    expect(pdfaLink).toHaveAttribute("target", "_blank");
  });
});
