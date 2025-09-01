import React from "react";
import { useRouter } from "next/router";
import { Space, Tag } from "antd";
import { usePathname } from "next/navigation";

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
  const pathname = usePathname()

  const getFilterArray = (val: string | string[] | undefined): string[] => {
    if (!val) return [];
    return Array.isArray(val) ? val : [val];
  };

  const filterKeys = ["country", "journal", "publication_year__lte", "publication_year__gte"];

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
      pathname,
      query: newQuery,
    });
  };

  const resertSearch = () => {
    router.push({
      pathname,
      query: {},
    });
  };

  const KEY_TO_TAGNAME: { [key: string]: string } = {
    "publication_year__lte": "pub year <",
    "publication_year__gte": "pub year >",
  }

  return (
    <Space wrap size={1} style={{ marginTop: "8px" }}>
      {filterKeys.flatMap((key) =>
        getFilterArray(query[key])?.map((val) => (
          <Tag
            key={`${key}-${val}`}
            closable
            bordered={false}
            onClose={() => handleRemove(key, val)}
          >
            {KEY_TO_TAGNAME[key] ? KEY_TO_TAGNAME[key] : `${key} : `} {val}
          </Tag>
        ))
      )}
      {filterKeys.flatMap((key) =>
        getFilterArray(query[`${key}__term`])?.map((val) => (
          <Tag
            key={`${key}__term-${val}`}
            closable
            bordered={false}
            onClose={() => handleRemove(`${key}__term`, val)}
          >
            {KEY_TO_TAGNAME[key] ? KEY_TO_TAGNAME[key] : `${key} : `} {val}
          </Tag>
        ))
      )}
      {Object.keys(query).length > 0 &&
        <Tag
          key={`reset-search`}
          closable
          color="#ccc"
          bordered={false}
          onClose={resertSearch}
        >
          Reset search
        </Tag>}
    </Space>
  );
};

export default SelectedFilters;
