import React from "react";
import { Text } from "react-mathjax2";

import { ArticleIdentifier, Result } from "@/types";
import PublicationInfo from "../shared/PublicationInfo";
import Authors from "../shared/Authors";
import {
  cleanText,
  renderComplexSytnax,
  resolveIdentifierLink,
} from "@/utils/utils";
import FulltextFiles from "../shared/FulltextFiles";

interface ResultItemProps {
  article: Result;
}

const ResultItem: React.FC<ResultItemProps> = ({ article }) => {
  const renderIdentifierLinks = (identifiers: ArticleIdentifier[]) => {
    return identifiers.map((identifier) => (
      <span key={identifier?.identifier_type}>
        {identifier?.identifier_type}:{" "}
        <a href={resolveIdentifierLink(identifier)}>
          {identifier?.identifier_value}
        </a>{" "}
      </span>
    ));
  };

  return (
    <li className="search-results-record border-0 border-b border-solid border-slate-200 py-6">
      <a href={`/records/${article?.id}`} className="mb-2 block text-lg">
        <Text
          text={
            <span
              dangerouslySetInnerHTML={{
                __html: renderComplexSytnax(cleanText(article?.title)),
              }}
            />
          }
        />
      </a>
      <div className="mb-2">
        <Authors authors={article?.authors} page="search" />
        <small className="search-results-record-date">
          {" "}
          - {article?.publication_date}
        </small>
      </div>
      <Text
        text={
          <p
            className="search-results-record-abstract mb-4"
            dangerouslySetInnerHTML={{
              __html: renderComplexSytnax(cleanText(article?.abstract)),
            }}
          />
        }
      />
      <div className="lg:flex justify-between items-end">
        <div>
          <span className="text-sm">Published in: </span>
          <PublicationInfo
            data={article?.publication_info?.[0]}
            page="search"
          />
          <p className="text-sm">
            {renderIdentifierLinks(article?.article_identifiers)}
          </p>
        </div>
        <div className="flex justify-end mt-2">
          <FulltextFiles files={article?.related_files} size="small" />
        </div>
      </div>
    </li>
  );
};

export default ResultItem;
