import React, { PropsWithChildren } from "react";

import { Context } from "react-mathjax2";

const MathjaxContext = ({ children }: PropsWithChildren) => (
  <Context
    script="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML"
    options={{
      asciimath2jax: {
        useMathMLspacing: true,
        delimiters: [
          ["$", "$"],
          ["$$", "$$"],
        ],
        preview: "none",
      },
      tex2jax: {
        inlineMath: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        processEscapes: true,
      },
    }}
  >
    {children}
  </Context>
);

export default MathjaxContext
