import { render, screen } from "@testing-library/react";

import HomePage from "@/pages/index";
import { facets } from "@/mocks/index";

describe("HomePage", () => {
  it("renders homepage with correct articles count", () => {
    const { container } = render(<HomePage count={4321} facets={facets} />);

    expect(container).toMatchSnapshot();
    expect(screen.getByText("4321 Open Access")).toBeInTheDocument();
    expect(
      screen.getByText("Journal of High Energy Physics")
    ).toBeInTheDocument();
    expect(screen.getByText("666")).toBeInTheDocument();
  });

  it("renders correct information in Journals tab", () => {
    render(<HomePage count={4321} facets={facets} />);

    expect(
      screen.getByText("Journal of High Energy Physics")
    ).toBeInTheDocument();
    expect(screen.getByText("666")).toBeInTheDocument();
  });

  it("renders correct information in Partners tab", () => {
    render(<HomePage count={4321} facets={facets} activeTabKey="2" />);

    expect(screen.getByText("Poland")).toBeInTheDocument();
    expect(screen.getByText("2137")).toBeInTheDocument();
  });
});
