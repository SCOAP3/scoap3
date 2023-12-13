import React from "react";
import { render, screen } from "@testing-library/react";
import PublicationInfo from "../PublicationInfo";

const mockData = {
  journal_title: "Sample Journal",
  journal_volume: "5",
  journal_issue: "02",
  volume_year: "2022",
  page_start: "25",
  page_end: "40",
  publisher: "Sample Publisher",
  artid: "1234",
  journal_issue_date: null
};

describe("PublicationInfo", () => {
  it("renders publication information correctly", () => {
    render(<PublicationInfo data={mockData} page="search" />);

    expect(screen.getByText("Sample Journal")).toBeInTheDocument();
    expect(screen.getByText(", Volume 5")).toBeInTheDocument();
    expect(screen.getByText("Issue 2")).toBeInTheDocument();
    expect(screen.getByText("Pages 25-40")).toBeInTheDocument();
    expect(screen.getByText("Sample Publisher")).toBeInTheDocument();

    expect(screen.getByText("Sample Journal")).toHaveClass(
      "publication-info-title"
    );
    expect(screen.getByText(", Volume 5")).toHaveClass(
      "publication-info-volume"
    );
    expect(screen.getByText("(2022)")).toHaveClass(
      "publication-info-volume_year"
    );
    expect(screen.getByText("Issue 2")).toHaveClass(
      "publication-info-issue"
    );
    expect(screen.getByText("Pages 25-40")).toHaveClass(
      "publication-info-pages"
    );
  });
});
