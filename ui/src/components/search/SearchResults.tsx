import React from "react";
import { Select } from "antd";
import { DownOutlined } from "@ant-design/icons";

import { Result } from "@/types";
import ResultItem from "./ResultItem";
import SearchPagination from "./SearchPagination";
import { useRouter } from "next/navigation";
import { getSearchUrl, getApiUrl } from "@/utils/utils";
import MathjaxContext from "../shared/MathjaxContext";

interface SearchResultsProps {
  results: Result[];
  count: number;
  params: any;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  count,
  params,
}) => {
  const router = useRouter();

  const sortOptions = [
    {
      label: "Most recent",
      value: "-publication_date",
    },
    {
      label: "Least recent",
      value: "publication_date",
    },
  ];

  const sortResults = (value: string) => {
    router.push(
      getSearchUrl({
        ...params,
        page: 1,
        ordering: value,
      })
    );
  };

  const downloadUrl = () => {
    let exportSearchParams = getSearchUrl({
      ...params,
      all: true,
      format: "csv"
    })
    const export_search_url = getApiUrl() + "/" + exportSearchParams;
    return export_search_url;
  }

  return (
    <div>
      <div className="mt-4 mb-6 flex justify-center md:justify-between items-center flex-col md:flex-row">
        <p className="flex items-center md:mb-0 mb-3">
          <a href={downloadUrl()} download="scoap3-search-export" >Found {count} results.</a>
        </p>
        <SearchPagination count={count} params={params} />
        <div className="sort flex items-center">
          {count > 0 && (
            <div>
              Sort by
              <Select
                options={sortOptions}
                className="sort-dropdown ml-3"
                onChange={sortResults}
                defaultValue="-publication_date"
              >
                <Select.OptGroup>
                  <DownOutlined />
                </Select.OptGroup>
              </Select>
            </div>
          )}
        </div>
      </div>
      <MathjaxContext>
        <ul className="border-0 border-t border-solid border-slate-200">
          {results &&
            results?.length > 0 &&
            results?.map((article: any) => (
              <ResultItem key={article?.id} article={article} />
            ))}
        </ul>
      </MathjaxContext>
      <div className="flex justify-center mb-7">
        <SearchPagination count={count} params={params} />
      </div>
    </div>
  );
};

export default SearchResults;
