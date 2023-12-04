import React from "react";
import ReactHtmlParser from "react-html-parser";
import { GetServerSideProps } from "next";
import { MathJax } from "better-react-mathjax";

import { Result } from "@/types";
import Authors from "@/components/shared/Authors";
import DetailPageInfo from "@/components/detail/DetailPageInfo";
import { authToken, getApiUrl } from "@/utils/utils";
import { JsonPreview } from "@/components/shared/JsonPreview";

interface RecordPageProps {
  article: Result;
}

const RecordPage: React.FC<RecordPageProps> = ({ article }) => {
  return (
    <div className="container grid grid-cols-4 gap-8">
      <div id="abstract_and_preview" className="col-span-3">
        <div id="abstract">
          <div className="detail-page-main">
            <h2 className="font-normal mb-3">
              <MathJax inline>{ReactHtmlParser(article?.title)}</MathJax>
            </h2>
            <Authors
              authors={article?.authors}
              page="detail"
              affiliations
              className="mb-3"
            />
            <p className="text-justify leading-relaxed">
              <MathJax inline>{ReactHtmlParser(article?.abstract)}</MathJax>
            </p>
          </div>
        </div>
        <div id="preview">
          <JsonPreview article={article} />
        </div>
      </div>
      <div id="abstract_and_preview" className="col-span-1 detail-page-right">
        <DetailPageInfo article={article} />
      </div>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const recordId = context.query["recordId"];

  const res = await fetch(getApiUrl() + `/${recordId}`, authToken);
  const article = (await res.json()) as Result;

  return { props: { article } };
};

export default RecordPage;
