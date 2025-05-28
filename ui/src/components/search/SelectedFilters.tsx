import React from "react";
import { useRouter } from "next/router";
import { Tag } from "antd";

interface Params {
  country?: string[] | string;
  journal?: string[] | string;
  _filter_publication_year?: string[] | string;
  [key: string]: any;
}

interface SelectedFiltersProps {
  query: Params;
}

const SelectedFilters: React.FC<SelectedFiltersProps> = ({ query }) => {
  const router = useRouter();

  const getFilterArray = (val: string | string[] | undefined): string[] => {
    if (!val) return [];
    return Array.isArray(val) ? val : [val];
  };

  const filterKeys = ["country", "journal", "_filter_publication_year"];

  const handleRemove = (filterKey: string, value: string) => {
    const newQuery = { ...query };
    const values = getFilterArray(newQuery[filterKey]);

    const updatedValues = values.filter((v) => v !== value);
    if (updatedValues.length === 0) {
      delete newQuery[filterKey];
    } else {
      newQuery[filterKey] = updatedValues;
    }

    router.push({
      pathname: "/search",
      query: newQuery,
    });
  };

  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', margin: '1rem 0' }}>
      {filterKeys.flatMap((key) =>
        getFilterArray(query[key])?.map((val) => (
          <Tag
            key={`${key}-${val}`}
            closable
            onClose={() => handleRemove(key, val)}
          >
            {val}
          </Tag>
        ))
      )}
    </div>
  );
};

export default SelectedFilters;
