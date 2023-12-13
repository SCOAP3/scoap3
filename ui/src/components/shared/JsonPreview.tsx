import React from "react";
import { Collapse } from "antd";

import { Result } from "@/types";

interface JsonPreviewProps {
  article: Result;
}

export const JsonPreview = ({ article }: JsonPreviewProps) => {
  return (
    <Collapse
      className="mt-5"
      items={[
        {
          key: "1",
          label: "Metadata preview. Preview of JSON metadata for this article.",
          children: (
            <p className="p-8 json-preview-content">
              <pre className="whitespace-pre-wrap font-mono text-sm leading-relaxed">
                {JSON.stringify(article, undefined, 2)}
              </pre>
            </p>
          ),
        },
      ]}
    />
  );
};
