import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { useSearchParams, useRouter } from "next/navigation";

import SearchBar from "../SearchBar";

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

const mockPush = jest.fn();
const mockGet = jest.fn();

(useRouter as jest.Mock).mockImplementation(() => ({
  push: mockPush,
}));
(useSearchParams as jest.Mock).mockReturnValue({
  get: mockGet,
});

describe("SearchBar", () => {
  it("renders search bar with placeholder", () => {
    render(<SearchBar placeholder="Search Articles" />);

    expect(screen.getByPlaceholderText("Search Articles")).toBeInTheDocument();
  });

  it("updates search value and triggers search on button click", async () => {
    render(<SearchBar />);

    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "Karolinka" },
    });

    await waitFor(() => {
      fireEvent.click(screen.getByRole("button"));
    });

    expect(mockPush).toHaveBeenCalledWith(
      "/search?page=1&page_size=20&search=Karolinka"
    );
  });
});
