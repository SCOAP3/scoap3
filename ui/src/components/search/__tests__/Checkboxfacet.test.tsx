import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";

import CheckboxFacet from "../CheckboxFacet";

describe("CheckboxFacet", () => {
  const mockData = [
    { key: "Item 1", doc_count: 5 },
    { key: "Item 2", doc_count: 10 },
    { key: "Item 3", doc_count: 15 },
    { key: "Item 4", doc_count: 20 },
    { key: "Item 5", doc_count: 25 },
    { key: "Item 6", doc_count: 30 },
    { key: "Item 7", doc_count: 35 },
    { key: "Item 8", doc_count: 40 },
    { key: "Item 9", doc_count: 45 },
    { key: "Item 10", doc_count: 50 },
    { key: "Item 11", doc_count: 55 },
    { key: "Item 12", doc_count: 60 },
    { key: "Item 13", doc_count: 65 },
    { key: "Item 14", doc_count: 70 },
  ];

  const mockParams = {
    country: "SelectedCountry",
  };

  it("renders checkbox facet correctly", () => {
    render(
      <CheckboxFacet
        type="country"
        title="Country"
        params={mockParams}
        data={mockData}
      />
    );

    expect(screen.getByText("Country")).toBeInTheDocument();
    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });

  it("triggers the correct state change when clicking on a checkbox ", () => {
    render(
      <CheckboxFacet
        type="country"
        title="Country"
        params={mockParams}
        data={mockData}
      />
    );

    const checkbox = screen.getByRole("checkbox", { name: "Item 1" });

    fireEvent.click(checkbox);

    expect(checkbox).toBeChecked();

    fireEvent.click(checkbox);

    expect(checkbox).not.toBeChecked();
  });


  it("displays additional items when clicking 'Show More' ", () => {
    render(
      <CheckboxFacet
        type="country"
        title="Country"
        params={mockParams}
        data={mockData}
      />
    );

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.queryByText("Item 14")).not.toBeInTheDocument();

    fireEvent.click(screen.getByText("Show More"));

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 14")).toBeInTheDocument();
  });

  it("hides additional items when clicking 'Show Less'", () => {
    render(
      <CheckboxFacet
        type="country"
        title="Country"
        params={mockParams}
        data={mockData}
      />
    );

    fireEvent.click(screen.getByText("Show More"));

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 14")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Show Less"));

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.queryByText("Item 14")).not.toBeInTheDocument();
  });
});
