import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { useRouter } from "next/navigation";

import ServerErrorPage from "@/pages/500";

jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

const mockPush = jest.fn();
(useRouter as jest.Mock).mockImplementation(() => ({
  push: mockPush,
}));

describe("ServerErrorPage", () => {
  it("renders error page", () => {
    const { container } = render(<ServerErrorPage />);

    expect(container).toMatchSnapshot();
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
    expect(screen.getByTestId("go-back")).toBeInTheDocument();
  });

  it("triggers router.push on 'go to home page' button click", () => {
    render(<ServerErrorPage />);

    fireEvent.click(screen.getByTestId("go-back"));

    expect(mockPush).toHaveBeenCalledWith("/");
  });
});
