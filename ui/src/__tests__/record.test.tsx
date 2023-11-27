import React from "react";
import { render, screen } from "@testing-library/react";
import { MathJaxContext } from "better-react-mathjax";

import RecordPage from "@/pages/records/[recordId]";
import { record } from "@/mocks/index";

describe("RecordPage", () => {
  it("renders article details correctly", () => {
    const { container } = render(
      <MathJaxContext>
        <RecordPage article={record} />
      </MathJaxContext>
    );

    expect(container).toMatchSnapshot();
    expect(
      screen.getByText(
        "Strings from 3D gravity: asymptotic dynamics of AdS 3 gravity with free boundary conditions"
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Pure three-dimensional gravity in anti-de Sitter space can be formulated as an SL(2 , R ) × SL(2 , R ) Chern-Simons theory, and the latter can be reduced to a WZW theory at the boundary. In this paper we show that AdS 3 gravity with free boundary conditions is described by a string at the boundary whose target spacetime is also AdS 3 . While boundary conditions in the standard construction of Coussaert, Henneaux, and van Driel are enforced through constraints on the WZW currents, we find that free boundary conditions are partially enforced through the string Virasoro constraints."
      )
    ).toBeInTheDocument();
  });
});
