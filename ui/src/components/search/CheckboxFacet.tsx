import React, { useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Card } from "antd";

import { Country, Journal } from "@/types";
import OperatorSwitch from "./OperatorSwitch";

interface CheckboxFacetProps {
  type: "country" | "journal";
  title: string;
  data: Country[] | Journal[];
}

const SEARCH_OPERATORS = {
  "country": ["OR", "AND"],
  "journal": ["OR"]
}

const CheckboxFacet: React.FC<CheckboxFacetProps> = ({
  type,
  title,
  data,
}) => {
  const [filters, setFilters] = useState<any[]>([]);
  const [showMore, setShowMore] = useState(false);
  const displayedData = showMore ? data : data?.slice(0, 13);
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname()
  const andQueries = searchParams.getAll(`${type}__term`);
  const [mode, setMode] = useState<"OR" | "AND">(andQueries.length > 0 ? "AND" : "OR");

  const createQueryString = useCallback(
    (name: string, value: any, mode = "OR") => {
      const params = new URLSearchParams(searchParams.toString())

      params.delete(name);
      params.delete(`${name}__term`);
      params.delete("page");

      if (!Array.isArray(value)) value = [value];

      const query_name = mode == "OR" ? name : `${name}__term`;
      value.forEach((val: string) => {
        params.append(query_name, val);
      });

      return params.toString()
    },
    [searchParams, mode]
  );

  useEffect(() => {
    const orQueries = searchParams.getAll(type);
    const andQueries = searchParams.getAll(`${type}__term`);

    setFilters([...orQueries, ...andQueries]);
  }, [searchParams]);

  const shortJournalName = (value: string) => {
    const journalMapping: Record<string, string> = {
      "Journal of Cosmology and Astroparticle Physics":
        "J. Cosm. and Astroparticle P.",
      "Advances in High Energy Physics": "Adv. High Energy Phys.",
      "Progress of Theoretical and Experimental Physics":
        "Prog. of Theor. and Exp. Phys.",
      "Journal of High Energy Physics": "J. High Energy Phys.",
    };

    return journalMapping[value] || value;
  };

  const onCheckboxChange = (value: string) => {
    let updated_filters = [];

    if (filters.includes(value)) {
      updated_filters = filters.filter((item: string) => item !== value);
    } else {
      updated_filters = [...filters, value]
    }

    setFilters(updated_filters);
    router.push(pathname + '?' + createQueryString(type, updated_filters, mode))
  };

  const onLogicModeChange = (new_mode: "OR" | "AND") => {
    setMode(new_mode)
    router.push(pathname + '?' + createQueryString(type, filters, new_mode))
  }

  return (
    <Card title={title} className="search-facets-facet mb-5">
      <OperatorSwitch isToggleable={SEARCH_OPERATORS[type]?.length > 1} mode={mode} setMode={onLogicModeChange} />
      <div>
        {displayedData?.map((item) => (
          <div key={item?.key} className="flex items-center justify-between">
            <span>
              <input
                className="mr-1"
                type="checkbox"
                name={item?.key}
                checked={filters.includes(item?.key)}
                onChange={() => onCheckboxChange(item?.key)}
              />
              {shortJournalName(item?.key)}
            </span>
            <span className="badge dark">{item?.doc_count}</span>
          </div>
        ))}
      </div>
      {data && data?.length > 13 && (
        <div className="mt-2">
          <a onClick={() => setShowMore(!showMore)} className="ml-1">
            {showMore ? "Show Less" : "Show More"}
          </a>
        </div>
      )}
    </Card>
  );
};

export default CheckboxFacet;
