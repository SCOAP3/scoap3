import ReactHtmlParser from "react-html-parser";

import { ArticleIdentifier, Params } from "@/types";
import { PARTNER_COUNTRIES } from "./data";
import { Token } from "../../token";

export const BASE_URL =
  process.env.NEXT_API_BASE_URL || "https://repo.scoap3.org";
const SEARCH_URL = "/api/search/article";

export const authToken = Token
  ? {
      headers: {
        Authorization: Token,
      },
    }
  : {};

const buildSearchParams = (q: Params): string => {
  const searchParams = new URLSearchParams();

  // replace 'search' param with 'search_simple_query_string'
  if (q["search"]) q["search_simple_query_string"] = q["search"];

  Object.entries(q).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => searchParams.append(key, item));
    } else {
      searchParams.set(key, `${value}`);
    }
  });

  return searchParams.toString();
};

const getSearchUrl = (query: Params, local?: boolean) => {
  const searchParams = buildSearchParams(query);
  const path = local ? "/search" : "";
  const params = searchParams ? `?${searchParams}` : "";
  const url = `${path}${params}`;

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
const cleanText = (text: string) =>
  text.replace(/<\/?(p|italic|sup|i|inf)>/g, "") ?? "";

const renderComplexSytnax = (abstract: string) => {
  if (abstract.includes("<math")) {
    return abstract;
  }
  return ReactHtmlParser(abstract);
};

function filterCountries(
  countryObjects: { key: string; doc_count: number }[]
): { key: string; doc_count: number }[] {
  return countryObjects.filter((obj) => PARTNER_COUNTRIES.includes(obj.key));
}

function mapCountryNames(
  countryObjects: { key: string; doc_count: number }[]
): { key: string; doc_count: number }[] {
  const correctCountries = countryObjects.map((country) => {
    if (country.key === "Taiwan, Province of China") {
      country.key = "Taiwan";
    }
    if (country.key === "Korea, Republic of") {
      country.key = "South Korea";
    }
    return country;
  });

  correctCountries.sort((a, b) => a.key.localeCompare(b.key));
  return correctCountries;
}

export {
  getSearchUrl,
  getApiUrl,
  resolveIdentifierLink,
  cleanText,
  renderComplexSytnax,
  filterCountries,
  mapCountryNames,
};
