import React from "react";
import { GetServerSideProps } from "next";
import { Text } from "react-mathjax2";

import { Result } from "@/types";
import Authors from "@/components/shared/Authors";
import DetailPageInfo from "@/components/detail/DetailPageInfo";
import {
  authToken,
  cleanText,
  getApiUrl,
  renderComplexSytnax,
} from "@/utils/utils";
import { JsonPreview } from "@/components/shared/JsonPreview";

interface RecordPageProps {
  article: Result;
}

const RecordPage: React.FC<RecordPageProps> = ({ article }) => {
  return (
    <div className="container">
      <div className="container-inner">
        <div className="flex flex-col md:flex-row">
          <div className="detail-page-main">
            <Text
              text={
                <h2
                  className="font-normal mb-3"
                  dangerouslySetInnerHTML={{
                    __html: renderComplexSytnax(cleanText(article?.title)),
                  }}
                />
              }
            />
            <Authors
              authors={article?.authors}
              page="detail"
              affiliations
              className="mb-3"
            />
            <Text
              text={
                <p
                  className="text-justify leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: renderComplexSytnax(cleanText(article?.abstract)),
                  }}
                />
              }
            />
            <JsonPreview article={article} />
          </div>
          <div className="detail-page-right">
            <DetailPageInfo article={article} />
          </div>
        </div>
      </div>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const recordId = context.query["recordId"];
  const req = context?.req;
  const clientIp = req.headers["x-forwarded-for"] || req.socket.remoteAddress;

  const res = await fetch(getApiUrl() + `/${recordId}`, {
    "headers": {
      ...authToken?.headers,
      "X-Forwarded-For": clientIp as string,
    }
  });
  const article = (await res.json()) as Result;

  return { props: { article } };
};

export default RecordPage;
