import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import TabContent from "../TabContent";

describe("TabContent", () => {
  const mockData = [
    { key: "Item 1", doc_count: 5 },
    { key: "Item 2", doc_count: 10 },
  ];

  it("renders tab content correctly", () => {
    render(<TabContent data={mockData} type="journal" />);

    expect(screen.getByText("Item 1")).toBeInTheDocument();
    expect(screen.getByText("Item 2")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
  });

  it("triggers the correct journal link when clicking on an item", () => {
    render(<TabContent data={mockData} type="journal" />);

    userEvent.click(screen.getByText("Item 1"));

    expect(screen.getByText("Item 1")).toHaveAttribute("href", "/search?page=1&page_size=20&journal=Item 1");
  });

  it("triggers the correct country link when clicking on an item", () => {
    render(<TabContent data={mockData} type="country" />);

    userEvent.click(screen.getByText("Item 1"));

    expect(screen.getByText("Item 1")).toHaveAttribute("href", "/search?page=1&page_size=20&country=Item 1");
  });
});
