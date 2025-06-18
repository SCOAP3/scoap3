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
  const [filters, setFilters] = useState<any[]>([]);
  const [showMore, setShowMore] = useState(false);
  const [mode, setMode] = useState<"AND" | "OR">("AND");

  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname()

  const originalDataRef = useRef<Country[] | Journal[]>(data);
  const effectiveAllData = allData ?? originalDataRef.current;
  const isJournal = type === "journal";

  useEffect(() => {
    if (isJournal) {
      setMode("OR");
    }
  }, [isJournal]);

  useEffect(() => {
    const logicParam = searchParams.get(`${type}_logic`);
    const orMode = logicParam === "or";
    if (type === "country") {
      setMode(orMode ? "OR" : "AND");
    }

    const currentFilters = searchParams.getAll(type);
    setFilters(currentFilters);
  }, [searchParams, type]);

  const createQueryString = useCallback(
    (name: string, values: string[]) => {
      const params = new URLSearchParams(searchParams.toString());
      params.delete(name);
      params.delete("page");
      params.delete(`${name}_logic`);

      values.forEach((val) => params.append(name, val));

      if (type === "country") {
        if (mode === "OR" && values.length > 0) {
          params.set(`${name}_logic`, "or");
        }
      }
      return params.toString();
    },
    [searchParams, type, mode]
  );

  const onCheckboxChange = (value: string) => {
    const updated = filters.includes(value)
      ? filters.filter((f) => f !== value)
      : [...filters, value];
    setFilters(updated);
    router.push(`${pathname}?${createQueryString(type, updated)}`);
  };

  const toggleLogicMode = () => {
    if (isJournal) return;
    const newMode = mode === "AND" ? "OR" : "AND";
    setMode(newMode);
    setFilters([]);
    const params = new URLSearchParams(searchParams.toString());
    params.delete(type);
    params.delete(`${type}_logic`);
    if (newMode === "OR") {
      params.set(`${type}_logic`, "or");
    }
    router.push(`${pathname}?${params.toString()}`);
  };

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

  const isOrMode = mode === "OR";
  const currentData = isOrMode ? effectiveAllData : data;
  const displayedData = showMore ? currentData : currentData.slice(0, 13);

  const LogicModeDisplay = ({ isToggleable }: { isToggleable: boolean }) => (
    <Tooltip
      title={
        isOrMode
          ? "OR logic: Results match ANY selected filter."
          : "AND logic: Results match ALL selected filters."
      }
    >
      <div className="flex items-center justify-between mb-3 p-2 bg-gray-50 rounded cursor-help">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Filter Logic:</span>
          <Tag className="text-gray-500 bg-gray-100 border-gray-300 m-0">
            {isOrMode ? "OR" : "AND"}
          </Tag>
        </div>
        {isToggleable && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">AND</span>
            <Switch
              checked={isOrMode}
              onChange={toggleLogicMode}
              size="small"
            />
            <span className="text-xs text-gray-600">OR</span>
          </div>
        )}
      </div>
    </Tooltip>
  );

  return (
    <Card title={title} className="search-facets-facet mb-5">
      {type === "country" && <LogicModeDisplay isToggleable={true} />}

      {isJournal && <LogicModeDisplay isToggleable={false} />}

      <div>
        {displayedData?.map((item) => (
          <div key={item?.key} className="flex items-center justify-between">
            <span>
              <input
                className="mr-1"
                type="checkbox"
                checked={filters.includes(item?.key)}
                onChange={() => onCheckboxChange(item?.key)}
              />
              {isJournal ? shortJournalName(item?.key) : item?.key}
              </span>
            {!isOrMode && (
              <span className="badge dark">{(item as any)?.doc_count}</span>
            )}
          </div>
        ))}
      </div>
      {currentData?.length > 13 && (
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
