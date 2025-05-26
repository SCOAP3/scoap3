import React, { useCallback, useState } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Card } from "antd";

import { Country, Journal } from "@/types";

interface CheckboxFacetProps {
  type: "country" | "journal";
  title: string;
  data: Country[] | Journal[];
}

const CheckboxFacet: React.FC<CheckboxFacetProps> = ({
  type,
  title,
  data,
}) => {
  const [showMore, setShowMore] = useState(false);
  const displayedData = showMore ? data : data?.slice(0, 13);
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname()

  const filters = searchParams.getAll(type);

  const createQueryString = useCallback(
    (name: string, value: string[]) => {
      const params = new URLSearchParams(searchParams.toString());
      params.delete(name);
      params.delete("page");

      if (!Array.isArray(value)) value = [value];
      value.forEach((val: string) => {
        params.append(name, val);
      });

      return params.toString()
    },
    [searchParams]
  );

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
    let updatedFilters = filters.includes(value)
      ? filters.filter((item) => item !== value)
      : [...filters, value];

    router.push(pathname + "?" + createQueryString(type, updatedFilters));
  };

  return (
    <Card title={title} className="search-facets-facet mb-5">
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
