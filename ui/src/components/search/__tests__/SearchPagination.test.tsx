import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { useRouter } from "next/navigation";

import SearchPagination from "../SearchPagination";

const mockParams = {
  page: 2,
  page_size: 10,
};

const mockCount = 100;

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

const mockPush = jest.fn();
(useRouter as jest.Mock).mockImplementation(() => ({
  push: mockPush,
}));

describe("SearchPagination", () => {
  it("renders pagination correctly", () => {
    const { container } = render(
      <SearchPagination count={mockCount} params={mockParams} />
    );

    expect(container.querySelector(".ant-pagination")).toBeInTheDocument();
    expect(
      screen
        .getAllByRole("listitem")
        .find((listitem) => listitem.textContent === "2")
    ).toHaveClass("ant-pagination-item-active");
  });

  it("triggers the correct navigation when clicking on a page", () => {
    render(<SearchPagination count={mockCount} params={mockParams} />);

    fireEvent.click(
      screen
        .getAllByRole("listitem")
        .find((listitem) => listitem.textContent === "3")!
    );

    expect(mockPush).toHaveBeenCalledWith("?page=3&page_size=10");
  });
});
