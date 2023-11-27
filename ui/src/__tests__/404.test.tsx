import { render, screen } from "@testing-library/react";

import PageNotFound from "@/pages/404";

describe("PageNotFound", () => {
  it("renders 404 page", () => {
    const { container } = render(<PageNotFound />);

    expect(container).toMatchSnapshot();
    expect(screen.getByText("Page not found")).toBeInTheDocument();
  });
});
