import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import YearFacet from "../YearFacet";
import { PublicationYear } from "@/types";

describe("YearFacet", () => {
  const mockData = [
    { key: "2021", doc_count: 5 },
    { key: "2022", doc_count: 10 },
    { key: "2023", doc_count: 15 },
  ] as never as PublicationYear[];

  const mockParams = {
    publication_year__range: "2021__2023",
  };

  it("renders year facet correctly", () => {
    render(<YearFacet data={mockData} params={mockParams} />);

    expect(screen.getByText("Year")).toBeInTheDocument();
    expect(screen.getByText("2021")).toBeInTheDocument();
    expect(screen.getByText("2023")).toBeInTheDocument();
  });

  it("displays the correct hint when hovering on a bar", () => {
    const { container } = render(
      <YearFacet data={mockData} params={mockParams} />
    );

    fireEvent.mouseOver(container.querySelector("rect")!);

    expect(screen.getByText("5")).toBeInTheDocument();

    fireEvent.mouseOut(container.querySelector("rect")!);

    expect(screen.queryByText("5")).not.toBeInTheDocument();
  });

  it("shows reset button after clicking on a bar", () => {
    const { container } = render(
      <YearFacet data={mockData} params={mockParams} />
    );

    fireEvent.click(container.querySelector("rect")!);

    expect(screen.getByText("Reset")).toBeInTheDocument();
  });
});
