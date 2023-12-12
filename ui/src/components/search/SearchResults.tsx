import React from "react";
import { Select } from "antd";
import { DownOutlined } from "@ant-design/icons";

import { Result } from "@/types";
import ResultItem from "./ResultItem";
import SearchPagination from "./SearchPagination";
import { useRouter } from "next/navigation";
import { getSearchUrl } from "@/utils/utils";

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
      value: "_updated_at",
    },
    {
      label: "Least recent",
      value: "-_updated_at",
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

  return (
    <div>
      <div className="mt-4 mb-6 flex justify-between align-center">
        <p className="flex items-center">Found {count} results.</p>
        <SearchPagination count={count} params={params} />
        <div className="sort flex items-center">
          {count > 0 && (
            <Select
              options={sortOptions}
              placeholder="Sort by"
              className="sort-dropdown"
              onChange={sortResults}
            >
              <div>
                Sort by <DownOutlined />
              </div>
            </Select>
          )}
        </div>
      </div>
      <ul className="border-0 border-t border-solid border-slate-200">
        {results &&
          results?.length > 0 &&
          results?.map((article: any) => (
            <ResultItem key={article?.id} article={article} />
          ))}
      </ul>
      <div className="flex justify-center">
        <SearchPagination count={count} params={params} />
      </div>
    </div>
  );
};

export default SearchResults;
