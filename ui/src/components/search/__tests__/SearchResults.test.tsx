import React from "react";
import { render, screen } from "@testing-library/react";
import SearchResults from "../SearchResults";
import { Params, Result } from "@/types";

const mockResults = [
  { id: "1", title: "Result 1" },
  { id: "2", title: "Result 2" },
] as never as Result[];

const mockCount = 20;
const mockParams = {
  page: 1,
  page_size: 10,
};

jest.mock("../ResultItem", () => ({ article }: { article: Result} ) => (
  <div data-testid={`result-item-${article.id}`}>{article.title}</div>
));

jest.mock("../SearchPagination", () => ({
  count,
  params,
}: {
  count: number
  params: Params
}) => <div data-testid="search-pagination">{`${count} results, page ${params.page}`}</div>);

describe("SearchResults", () => {
  it("renders search results correctly", () => {
    const { container } = render(<SearchResults results={mockResults} count={mockCount} params={mockParams} />);

    expect(screen.getByText("Found 20 results.")).toBeInTheDocument();
    expect(screen.getByTestId("result-item-1")).toBeInTheDocument();
    expect(screen.getByTestId("result-item-2")).toBeInTheDocument();
    expect(container.querySelector("[data-testid='search-pagination']")).toBeInTheDocument();
  });
});
