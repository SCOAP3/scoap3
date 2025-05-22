import React from "react";
import { GetServerSideProps } from "next";

import { Facets, Params, Result } from "@/types";
import SearchBar from "@/components/shared/SearchBar";
import SearchResults from "@/components/search/SearchResults";
import YearFacet from "@/components/search/YearFacet";
import { authToken, getApiUrl} from "@/utils/utils";
import CheckboxFacet from "@/components/search/CheckboxFacet";
import ResetSearchButton from "@/components/search/ResetSearchButton";
import { encode } from 'querystring';

interface SearchPageProps {
  results: Result[];
  count: number;
  facets: Facets;
  query: Params;
}

const SearchPage: React.FC<SearchPageProps> = ({
  results,
  count,
  query,
  facets,
}) => {
  const years = facets?._filter_publication_year?.publication_year?.buckets;
  const countries = facets?._filter_country?.country?.buckets;
  const journals = facets?._filter_journal?.journal?.buckets;

  const hasSelectedCountries = query.country && (Array.isArray(query.country) ? query.country.length > 0 : true);
  const hasSelectedJournals = query.journal && (Array.isArray(query.journal) ? query.journal.length > 0 : true);

  const showCountryFacet = (countries && countries.length > 0) || hasSelectedCountries;
  const showJournalFacet = (journals && journals.length > 0) || hasSelectedJournals;

  return (
    <div className="container">
      <div className="container-inner">
        <div className="search flex">
          <div className="search-facets">
            {results && results.length > 0 && years && years.length > 0 && (
              <YearFacet data={years} params={query} />
            )}

            {showCountryFacet && (
              <CheckboxFacet
                data={countries || []}
                title="Country / Region / Territory"
                type={"country"}
              />
            )}

            {showJournalFacet && (
              <CheckboxFacet
                data={journals || []}
                title="Journal"
                type={"journal"}
              />
            )}
          </div>
          <div className="search-results">
            <div className="flex items-center gap-3 mb-4">
              <SearchBar className="search-results-searchbar flex-1" />
              <ResetSearchButton />
            </div>
            <SearchResults results={results} count={count} params={query} />
          </div>
        </div>
      </div>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const query = context?.query as unknown as Params;
  const req = context?.req;

  const clientIp = req.headers["x-forwarded-for"] || req.socket.remoteAddress;
  const searchParams = new URLSearchParams(encode(query))
  const params = searchParams ? `?${searchParams}` : "";
  const url = getApiUrl() + params
  let results = [], count = 0, facets = [];

  try {
    const res = await fetch(url, {
      "headers": {
        ...authToken?.headers,
        "X-Forwarded-For": clientIp as string,
      }
    });

    const contentType = res.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
      const data = await res.json();
      results = data.results;
      count = data.count;
      facets = data.facets;
    }
  } catch (err) {
    console.error("Error fetching or parsing data:", err);
  }



  return {
    props: { results, count, query, facets },
  };
};

export default SearchPage;
