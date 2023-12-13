/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card } from "antd";

import { getSearchUrl } from "@/utils/utils";
import { Country, Journal, Params } from "@/types";

interface CheckboxFacetProps {
  type: "country" | "journal";
  title: string;
  params: Params;
  data: Country[] | Journal[];
}

const CheckboxFacet: React.FC<CheckboxFacetProps> = ({
  type,
  title,
  params,
  data,
}) => {
  const [filters, setFilters] = useState<any[]>([]);
  const [showMore, setShowMore] = useState(false);
  const displayedData = showMore ? data : data?.slice(0, 13);
  const router = useRouter();

  useEffect(() => {
    setFilters([params[type]].flat());
  }, []);

  useEffect(() => {
    router.push(getSearchUrl({ ...params, page: 1, [type]: filters }));
  }, [filters]);

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
    if (filters.includes(value)) {
      const newFilters = filters.filter((item: string) => item !== value);
      setFilters(newFilters);
    } else {
      setFilters((oldFilters) => [...oldFilters, value]);
    }
  };

  return (
    <Card title={title} className="search-facets-facet mb-5">
      <div>
        {displayedData?.map((item) => (
          <div key={item?.key} className="flex items-center justify-between">
            <label>
              <input
                className="mr-1"
                type="checkbox"
                name={item?.key}
                checked={filters.includes(item?.key)}
                onChange={() => onCheckboxChange(item?.key)}
              />
              {shortJournalName(item?.key)}
            </label>
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
