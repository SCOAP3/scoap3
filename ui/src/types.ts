export const queryTypes = [
  "page",
  "page_size",
  "search",
  "country",
  "journal",
  "publication_year__range",
  "ordering"
] as const;

export type QueryType = (typeof queryTypes)[number];

export type Params = {
  page?: number;
  page_size?: number;
  search?: string;
  country?: string | string[];
  journal?: string | string[];
  publication_year__range?: string;
};

export interface Response {
  count: number;
  next: string;
  previous: string;
  facets: Facets;
  results: Result[];
}

export interface Result {
  _created_at: string;
  title: string;
  first_online_date: Date | null;
  acceptance_date: Date | null;
  abstract: string;
  publication_info: JournalInfo[];
  related_files: File[];
  related_materials: [];
  related_licenses: License[];
  publication_date: string;
  id: number;
  authors: Author[];
  article_identifiers: ArticleIdentifier[];
  subtitle: string;
  reception_date: Date | null;
  article_arxiv_category: ArxivCategory[];
  copyright: Copyright[];
}

export interface Facets {
  _filter_publication_year: {
    doc_count: number;
    publication_year: {
      buckets: PublicationYear[];
    };
  };
  _filter_country: {
    doc_count: number;
    country: {
      buckets: Country[];
    };
  };
  _filter_journal: {
    doc_count: number;
    journal: {
      buckets: Journal[];
    };
  };
}

export interface Copyright {
  statement: string;
  year: string;
  holder: string;
}
export interface ArxivCategory {
  category: string;
  primary: boolean;
}

export interface ArticleIdentifier {
  identifier_type: 'DOI' | 'arXiv';
  identifier_value: string;
}

export interface Affiliation {
  value: string;
  organization: string;
  country: {
    code: string;
    name: string;
  };
}
export interface Author {
  first_name: string;
  last_name?: string;
  affiliations?: Affiliation[];
  orcid?: string;
}

export interface License {
  url: string;
  name: string;
}

export interface File {
  file: string;
  created: Date;
  updated: Date;
}

export interface JournalInfo {
  journal_volume: string;
  journal_title: string;
  journal_issue: string;
  page_start: number;
  page_end: number;
  artid: number;
  volume_year: number;
  journal_issue_date: Date | null;
  publisher: string;
}

export interface Journal {
  key: string;
  doc_count: number;
}

export interface Country {
  key: string;
  doc_count: number;
}

export interface PublicationYear {
  key: string;
  doc_count: number;
}

export interface MenuItem {
  key: string;
  label: JSX.Element | JSX.Element[] | string;
}

export type Extension = "pdf" | "pdfa" | "xml";

export const supportedExtensions: Extension[] = ["pdf", "pdfa", "xml"];

export interface YearFacetData {
  // year
  x: number;
  // count
  y: number;
}
