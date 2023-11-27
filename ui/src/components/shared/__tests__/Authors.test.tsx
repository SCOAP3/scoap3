import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import Authors from "../Authors";
import { authors } from "@/mocks/index";

describe("Authors", () => {
  it("renders authors correctly in search page", () => {
    render(<Authors authors={authors} page="search" />);

    expect(screen.getByText("Doe, John")).toBeInTheDocument();
    expect(screen.getByText("Smith, Jane")).toBeInTheDocument();
    expect(screen.getByTitle("1234-5678-9101-1126")).toBeInTheDocument();
    expect(screen.getByTitle("9876-5432-1098-7658")).toBeInTheDocument();
  });

  it("renders authors correctly in detail page", () => {
    render(<Authors authors={authors} page="detail" affiliations />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(
      screen.getByText("Affiliation 1, Affiliation 2")
    ).toBeInTheDocument();
    expect(screen.getByText("Affiliation 3")).toBeInTheDocument();
    expect(screen.getByTitle("1234-5678-9101-1126")).toBeInTheDocument();
    expect(screen.getByTitle("9876-5432-1098-7658")).toBeInTheDocument();
  });

  it("renders affiliations link correctly", () => {
    render(<Authors authors={authors} page="search" affiliations />);

    expect(
      screen.getByRole("link", { name: /Affiliation 1, Affiliation 2/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Affiliation 3/i })
    ).toBeInTheDocument();
  });

  it("renders Orcid links correctly", () => {
    render(<Authors authors={authors} page="search" />);

    expect(screen.getByTitle("1234-5678-9101-1126")).toHaveAttribute(
      "href",
      "https://orcid.org/1234-5678-9101-1126"
    );
    expect(screen.getByTitle("9876-5432-1098-7658")).toHaveAttribute(
      "href",
      "https://orcid.org/9876-5432-1098-7658"
    );
  });

  it("renders modal button correctly", () => {
    render(<Authors authors={authors} page="detail" />);

    expect(screen.getByText(/Show all 7 authors/i)).toBeInTheDocument();
  });

  it("opens and closes modal correctly", async () => {
    render(<Authors authors={authors} page="detail" affiliations />);

    expect(screen.getByText("et al")).toBeInTheDocument();
    expect(screen.queryByText("Michael Smith")).toBeNull();
    expect(screen.queryByText("Tom Jones")).toBeNull();

    fireEvent.click(screen.getByText(/Show all 7 authors/i));
    await waitFor(() =>
      expect(screen.getByText("Michael Smith")).toBeInTheDocument()
    );
    await waitFor(() =>
      expect(screen.getByText("Tom Jones")).toBeInTheDocument()
    );

    fireEvent.click(screen.getByRole("button", { name: /Close/i }));
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: /Close/i })).toBeNull()
    );
  });
});
