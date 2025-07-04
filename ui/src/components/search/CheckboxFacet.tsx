import React, { useState, useEffect, useCallback, useRef } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { Card, Switch, Tooltip, Tag } from "antd";

import { Country, Journal } from "@/types";

interface CheckboxFacetProps {
  type: "country" | "journal";
  title: string;
  data: Country[] | Journal[];
  allData?: Country[] | Journal[];
}

const CheckboxFacet: React.FC<CheckboxFacetProps> = ({
  type,
  title,
  data,
  allData,
}) => {
  const isJournal = type === "journal";

  const [filters, setFilters] = useState<string[]>([]);
  const [showMore, setShowMore] = useState(false);
  const [isOrMode, setIsOrMode] = useState(false);

  const effectiveIsOrMode = isJournal || isOrMode;

  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const enableLogicToggle = type === "journal" || type === "country";

  const originalDataRef = useRef<Country[] | Journal[]>(data);
  const effectiveAllData = allData ?? originalDataRef.current;

  const currentData = enableLogicToggle && effectiveIsOrMode
    ? effectiveAllData
    : data;
  const displayedData = showMore ? currentData : currentData.slice(0, 13);

  const createQueryString = useCallback(
    (name: string, values: string[], orMode: boolean = false) => {
      const params = new URLSearchParams(searchParams.toString());
      params.delete(name);
      params.delete(`${name}__term`);
      if (enableLogicToggle) {
        params.delete(`${name}_logic`);
      }
      params.delete("page");

      if (enableLogicToggle) {
        if (orMode) params.set(`${name}_logic`, "or");
        else params.delete(`${name}_logic`);
      }

      let paramKey = name;
      if (type === "country" && enableLogicToggle && !orMode) {
        paramKey = `${name}__term`;
      }

      values.forEach((val) => params.append(paramKey, val));
      return params.toString();
    },
    [searchParams, type, enableLogicToggle]
  );

  useEffect(() => {
    if (isJournal) {
      setIsOrMode(true);
      setFilters(searchParams.getAll(type));
    } else if (enableLogicToggle) {
      const logicParam = searchParams.get(`${type}_logic`);
      const or = logicParam === "or";
      setIsOrMode(or);
      const key = or ? type : `${type}__term`;
      setFilters(searchParams.getAll(key));
    } else {
      setIsOrMode(false);
      setFilters(searchParams.getAll(type));
    }
  }, [searchParams, type, enableLogicToggle, isJournal]);

  const shortJournalName = (value: string) => {
    const mapping: Record<string, string> = {
      "Journal of Cosmology and Astroparticle Physics": "J. Cosm. and Astroparticle P.",
      "Advances in High Energy Physics": "Adv. High Energy Phys.",
      "Progress of Theoretical and Experimental Physics": "Prog. of Theor. and Exp. Phys.",
      "Journal of High Energy Physics": "J. High Energy Phys.",
    };
    return mapping[value] || value;
  };

  const onCheckboxChange = (value: string) => {
    const updated = filters.includes(value)
      ? filters.filter((f) => f !== value)
      : [...filters, value];
    setFilters(updated);
    router.push(`${pathname}?${createQueryString(type, updated, effectiveIsOrMode)}`);
  };

  const toggleLogicMode = () => {
    if (isJournal) return;

    const newMode = !isOrMode;
    setIsOrMode(newMode);
    setFilters([]);
    router.push(`${pathname}?${createQueryString(type, [], newMode)}`);
  };

  const LogicModeButton = () => (
    <Tooltip
      title={
        effectiveIsOrMode
          ? "OR mode: Results match ANY selected filter. All filter options are available."
          : "AND mode: Results match ALL selected filters. Only filters with matching results are shown."
      }
    >
      <div className="flex items-center justify-between mb-3 p-2 bg-gray-50 rounded cursor-help">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Filter Logic:</span>
          <Tag className="text-gray-500 bg-gray-100 border-gray-300 m-0">
            {effectiveIsOrMode ? "OR" : "AND"}
          </Tag>
        </div>
        {!isJournal && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">AND</span>
            <Switch checked={isOrMode} onChange={toggleLogicMode} size="small" />
            <span className="text-xs text-gray-600">OR</span>
          </div>
        )}
      </div>
    </Tooltip>
  );

  return (
    <Card title={title} className="search-facets-facet mb-5">
      {enableLogicToggle && <LogicModeButton />}
      <div>
        {displayedData?.map((item) => (
          <div key={item?.key} className="flex items-center justify-between">
            <label className="flex items-center gap-1">
              <input
                type="checkbox"
                checked={filters.includes(item?.key)}
                onChange={() => onCheckboxChange(item?.key)}
              />
              {type === "journal" ? shortJournalName(item?.key) : item?.key}
            </label>
            {!(enableLogicToggle && effectiveIsOrMode) && (
              <span className="badge dark">{(item as any)?.doc_count}</span>
            )}
          </div>
        ))}
      </div>
      {currentData?.length > 13 && (
        <div className="mt-2">
          <a onClick={() => setShowMore(!showMore)} className="ml-1 cursor-pointer">
            {showMore ? "Show Less" : "Show More"}
          </a>
        </div>
      )}
    </Card>
  );
};

export default CheckboxFacet;
