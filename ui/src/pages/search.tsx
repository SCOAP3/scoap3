import React from "react";
import { GetServerSideProps } from "next";

import { Facets, Params, Response, Result } from "@/types";
import SearchBar from "@/components/shared/SearchBar";
import SearchResults from "@/components/search/SearchResults";
import YearFacet from "@/components/search/YearFacet";
import { authToken, getApiUrl, getSearchUrl } from "@/utils/utils";
import CheckboxFacet from "@/components/search/CheckboxFacet";

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

  return (
    <div className="container">
      <div className="container-inner">
        <div className="search flex">
          <div className="search-facets">
            {results && results.length > 0 && (
              <>
                {years && years.length > 0 && (
                  <YearFacet data={years} params={query} />
                )}
                {countries && countries.length > 0 && (
                  <CheckboxFacet
                    data={countries}
                    title="Country / Region / Territory"
                    type={"country"}
                    params={query}
                  />
                )}

                {journals && journals.length > 0 && (
                  <CheckboxFacet
                    data={journals}
                    title="Journal"
                    type={"journal"}
                    params={query}
                  />
                )}
              </>
            )}
          </div>
          <div className="search-results">
            <SearchBar className="search-results-searchbar" />
            <SearchResults results={results} count={count} params={query} />
          </div>
        </div>
      </div>
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const query = context?.query as unknown as Params;

  const res = await fetch(getApiUrl() + getSearchUrl({ ...query }), authToken);
  const { results, count, facets } = (await res.json()) as Response;

  return { props: { results, count, query, facets } };
};

export default SearchPage;
