import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { JsonPreview } from "../JsonPreview";
import { record } from "@/mocks/index";

describe("JsonPreview", () => {
  it("renders JSON preview correctly", async () => {
    render(<JsonPreview article={record} />);

    await waitFor(() =>
      userEvent.click(
        screen.getByText(
          "Metadata preview. Preview of JSON metadata for this article."
        )
      )
    );

    expect(
      screen.getByText(
        "Metadata preview. Preview of JSON metadata for this article."
      )
    ).toBeInTheDocument();
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "Strings from 3D gravity: asymptotic dynamics of AdS 3 gravity with free boundary conditions"
    );
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "Sundborg"
    );
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "2015-06-25"
    );
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "Springer/SISSA"
    );
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "Journal of High Energy Physics"
    );
    expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
      "10.1007/JHEP06(2015)171"
    );
  });

  it("collapses and expands the content correctly", async () => {
    render(<JsonPreview article={record} />);

    expect(screen.queryByTestId("json-preview-content")).toBeNull();

    userEvent.click(
      screen.getByText(
        "Metadata preview. Preview of JSON metadata for this article."
      )
    );

    await waitFor(() =>
      expect(screen.getByTestId("json-preview-content")?.textContent).toContain(
        "Strings from 3D gravity: asymptotic dynamics of AdS 3 gravity with free boundary conditions"
      )
    );
  });
});
