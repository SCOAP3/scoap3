import React from "react";
import { GetStaticPaths, GetStaticProps } from "next";
import Head from 'next/head';
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
import MathjaxContext from "@/components/shared/MathjaxContext";
import TitleWithSupport from "@/components/search/TitleWithSupport";

interface RecordPageProps {
  article: Result;
}

const getMetaPubInfo = (article: Result) => {
  if (article.publication_info.length > 0) {
    return [
      (article?.publication_info[0]?.page_start && article?.publication_info[0]?.page_end) ?
        [
          <meta key="page-start" name="citation_firstpage" content={`${article?.publication_info[0]?.page_start}`} />,
          <meta key="page-end" name="citation_lastpage" content={`${article?.publication_info[0]?.page_end}`} />
        ] : null,
      <meta key="citation_publisher" name="citation_publisher" content={article.publication_info[0]?.publisher} />,
      <meta key="citation_journal_title" name="citation_journal_title" content={article.publication_info[0]?.journal_title} />,
      <meta key="citation_journal_volume" name="citation_journal_volume" content={article.publication_info[0]?.journal_volume} />,
      <meta key="citation_journal_issue" name="citation_journal_issue" content={article.publication_info[0]?.journal_issue} />

    ]
  }
}

export default function RecordPage({ article }: RecordPageProps) {
  return (
    <>
      <Head >
        <title>{article.title}</title>


        <meta name="citation_abstract_html_url" content="{{ request.url }}" />

        {article?.article_identifiers?.map((identifier, idx) => {
          if (identifier?.identifier_type == "arXiv") {
            return (
              <meta key={idx} name="citation_technical_report_number" content={`${identifier?.identifier_value}`} />
            )
          }
        })}

        {article?.related_files?.map((file, idx) => {
          if (file?.file.indexOf(".pdf") > 0) {
            return (
              <meta key={idx} name="citation_pdf_url" content={`${file?.file}`} />
            )
          }
        })}

        <meta name="description" content={article.abstract} />
        <meta name="citation_title" content={article.title} />
        {article?.authors.map((author, idx) => <meta key={idx} name="citation_author" content={`${author?.last_name}, ${author?.first_name}`} />)}
        <meta name="citation_publication_date" content={article.publication_date.replace("-", "/")} />
        {getMetaPubInfo(article)}
        <meta name="citation_doi" content={article.doi} />
      </Head>
      <div className="container">
        <div className="container-inner">
          <div className="flex flex-col md:flex-row">
            <div className="detail-page-main">
              <TitleWithSupport title={article?.title} showExtra />
              <Authors
                authors={article?.authors}
                page="detail"
                affiliations
                className="mb-3"
              />
              <div
                className="text-justify leading-relaxed hidden"
                dangerouslySetInnerHTML={{
                  __html: renderComplexSytnax(cleanText(article?.abstract)),
                }}
              />
              <MathjaxContext>
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
              </MathjaxContext>

              <JsonPreview article={article} />
            </div>
            <div className="detail-page-right">
              <DetailPageInfo article={article} />
            </div>
          </div>
        </div>
      </div>
    </>
  )
};


export const getStaticPaths: GetStaticPaths = async () => {
  return {
    paths: [],
    fallback: 'blocking',
  };
};

export const getStaticProps: GetStaticProps = async (context) => {
  const recordId = context.params?.recordId;
  const res = await fetch(getApiUrl() + `/${recordId}`, {
    headers: {
      ...authToken?.headers,
    },
  });

  if (!res.ok) {
    return {
      notFound: true,
    };
  }

  const article = (await res.json()) as Result;

  return {
    props: { article },
    revalidate: 6000,
  };
};
