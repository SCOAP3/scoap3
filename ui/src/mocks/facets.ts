export const facets = {
  _filter_publication_year: {
    doc_count: 123,
    publication_year: {
      buckets: [
        {
          key: 1388534400000,
          doc_count: 2137,
        },
      ],
    },
  },
  _filter_country: {
    doc_count: 123,
    country: {
      buckets: [
        {
          key: "Poland",
          doc_count: 2137,
        },
      ],
    },
  },
  _filter_journal: {
    doc_count: 123,
    journal: {
      buckets: [
        {
          key: "Journal of High Energy Physics",
          doc_count: 666,
        },
      ],
    },
  },
};
