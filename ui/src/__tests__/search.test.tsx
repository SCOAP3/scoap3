import { render, screen } from "@testing-library/react";
import { MathJaxContext } from "better-react-mathjax";

import SearchPage from "@/pages/search";
import { facets, results, query } from "@/mocks/index";

describe("SearchPage", () => {
  it("renders search with correct articles count", () => {
    const { container } = render(
      <MathJaxContext>
        <SearchPage
          results={results}
          count={10}
          facets={facets}
          query={query}
        />
      </MathJaxContext>
    );

    expect(container).toMatchSnapshot();
    expect(screen.getByText("Found 10 results.")).toBeInTheDocument();
  });

  it("renders facets", () => {
    render(
      <MathJaxContext>
        <SearchPage
          results={results}
          count={10}
          facets={facets}
          query={query}
        />
      </MathJaxContext>
    );

    expect(screen.getByText("Year")).toBeInTheDocument();
    expect(
      screen.getByText("Country / Region / Territory")
    ).toBeInTheDocument();
    expect(screen.getByText("Journal")).toBeInTheDocument();
  });

  it("renders pagination if >20 results", () => {
    const { container } = render(
      <MathJaxContext>
        <SearchPage
          results={results}
          count={21}
          facets={facets}
          query={query}
        />
      </MathJaxContext>
    );

    const pagination = container.getElementsByClassName("ant-pagination");
    expect(pagination.length).toBe(2);
  });
});
