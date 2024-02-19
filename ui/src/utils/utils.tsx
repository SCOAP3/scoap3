import ReactHtmlParser from "react-html-parser";

import { ArticleIdentifier, Params, QueryType, queryTypes } from "@/types";
import { PARTNER_COUNTRIES } from "./data";
import { Token } from "../../token";

export const BASE_URL =
  process.env.NEXT_API_BASE_URL || "https://backend.dev.scoap3.org";
const SEARCH_URL = "/api/search/article";

export const authToken = Token
  ? {
      headers: {
        Authorization: Token,
      },
    }
  : {};

const defaultQueryValues = {
  page: 1,
  page_size: 20,
};

const isValue = (value: any): boolean =>
  value !== undefined && value !== null && value !== "";

const buildSearchParams = (q: Params): string => {
  const query = { ...defaultQueryValues, ...q };

  const values = Object.entries(query).flatMap(([key, value]) => {
    if (queryTypes.includes(key as QueryType)) {
      if (Array.isArray(value)) {
        return value.filter(isValue).map((v) => `${key}=${v}`);
      } else if (isValue(value)) {
        return [`${key}=${value}`];
      }
    }
    return [];
  });

  return values.join("&");
};

const getSearchUrl = (query: Params, local?: boolean) => {
  const searchParams = buildSearchParams(query);
  const url = local ? `/search?${searchParams}` : `?${searchParams}`;

  return url;
};

const getApiUrl = () => {
  return BASE_URL + SEARCH_URL;
};

const resolveIdentifierLink = (identifier: ArticleIdentifier) => {
  const { identifier_type, identifier_value } = identifier || {};

  switch (identifier_type) {
    case "DOI":
      return identifier_value ? `https://doi.org/${identifier_value}` : "/";
    case "arXiv":
      return identifier_value
        ? `https://arxiv.org/abs/${identifier_value}`
        : "/";
    default:
      return "/";
  }
};

// strip <p> and <italic> tags to resolve errors: <p> cannot appear as a descendant of <p> and <italic> is not a valid tag.
const cleanText = (text: string) => text.replace(/<\/?(p|italic|sup|i|inf)>/g, "") ?? "";

const renderComplexSytnax = (abstract: string) => {
  if (abstract.includes("<math")) {
    return abstract;
  }
  return ReactHtmlParser(abstract);
};

function filterCountries(
  countryObjects: { key: string; doc_count: number }[]
): { key: string; doc_count: number }[] {
  return countryObjects.filter(obj => PARTNER_COUNTRIES.includes(obj.key));
}

function mapCountryNames(
  countryObjects: { key: string; doc_count: number }[]
): { key: string; doc_count: number }[] {
  const correctCountries = countryObjects.map(country => {
    if (country.key === 'Taiwan, Province of China') {
      country.key = 'Taiwan';
    }
    if (country.key === 'Korea, Republic of') {
      country.key = 'South Korea';
    }
    return country;
  });

  correctCountries.sort((a, b) => a.key.localeCompare(b.key))
  return correctCountries;
}

export { getSearchUrl, getApiUrl, resolveIdentifierLink, cleanText, renderComplexSytnax, filterCountries, mapCountryNames };
