import React, { useEffect, useState, useCallback } from "react";
import { XYPlot, VerticalBarSeries, Hint } from "react-vis";
import { Button, Card, Slider } from "antd";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import "react-vis/dist/style.css";

import { PublicationYear, YearFacetData } from "@/types";


const mapInitialDataToYears = (
  initial: PublicationYear[]
): YearFacetData[] => {
  return initial?.map((item) => ({
    x: new Date(item?.key)?.getFullYear(),
    y: item?.doc_count,
  }));
};

const YearFacet = ({ data }: any) => {
  const [hoveredBar, setHoveredBar] = useState<any>(null);
  const [filters, setFilters] = useState<YearFacetData[]>([]);
  const [initialEndpoints, setInitialEndpoints] = useState<number[]>([]);
  const [sliderEndpoints, setSliderEndpoints] = useState<number[]>([]);

  const router = useRouter();
  const pathname = usePathname()
  const searchParams = useSearchParams();

  useEffect(() => {
    const initialData = mapInitialDataToYears(data);
    setFilters(initialData);
    const endpoints = getSliderEndpoints(initialData);
    setInitialEndpoints(endpoints);

    const hasYearFilters = searchParams.get('publication_year__gte') || searchParams.get('publication_year__lte');
    if (!hasYearFilters) {
      setSliderEndpoints(endpoints);
    }
  }, [data, searchParams]);

  useEffect(() => {
    const gteParam = searchParams.get('publication_year__gte');
    const lteParam = searchParams.get('publication_year__lte');

    if (gteParam && lteParam && initialEndpoints.length > 0) {
      const gteYear = parseInt(gteParam.split('-')[0]);
      const lteYear = parseInt(lteParam.split('-')[0]);
      setSliderEndpoints([gteYear, lteYear]);
    } else if (!gteParam && !lteParam && initialEndpoints.length > 0) {
      setSliderEndpoints(initialEndpoints);
    }
  }, [searchParams, initialEndpoints]);

  const resolveYearQuery = (name: string, params: any, range: number[]) => {
    if (range[0] === range[1]) {
      params.set(`${name}__gte`, range[0]?.toString()+"-01-01")
      params.set(`${name}__lte`, range[0]?.toString()+"-12-31")
      return range[0]?.toString();
    }
    params.set(`${name}__gte`, range[0]?.toString()+"-01-01")
    params.set(`${name}__lte`, range[1]?.toString()+"-12-31")
    return range.join("__");
  };

  const createQueryString = useCallback(
    (name: string, value: any) => {
      const params = new URLSearchParams(searchParams.toString())

      params.delete(`${name}__lte`);
      params.delete(`${name}__gte`);
      params.delete("page");
      resolveYearQuery(name, params, [value[0].x, value[1].x])

      return params.toString()
    },
    [searchParams]
  )

  const getSliderEndpoints = (initial: YearFacetData[]): number[] => {
    if (initial.length === 1) return [initial[0]?.x];
    return [initial[0]?.x, initial[initial.length - 1]?.x];
  };

  const onSliderChange = (data: number[]) => {
    setSliderEndpoints(data)
  };

  const onSliderAfterChange = (data: number[]) => {
    setSliderEndpoints(data)
    const params = createQueryString('publication_year',  [{x:data[0]}, {x:data[1]}]);
    router.push(pathname + (params ? `?${params.toString()}` : ""))
  };

  const onBarClick = (value: YearFacetData) => {
    const params = createQueryString('publication_year', [value, value]);
    router.push(pathname + (params ? `?${params.toString()}` : ""))
  };

  const onBarMouseHover = (bar: YearFacetData) => {
    setHoveredBar({ [bar.x]: bar.y });
  };

  const onBarMouseOut = () => setHoveredBar(null);

  const resetFilters = () => {
    const params = new URLSearchParams(searchParams.toString());
    params.delete('publication_year__lte');
    params.delete('publication_year__gte');
    params.delete('page');
    router.push(pathname + (params.toString() ? `?${params.toString()}` : ""))
  };

  let marks: any = {}
  filters.map(
    (i, idx) => {
      marks[`${i.x}`] = {
        label: idx == 0 || idx == filters.length-1 ? `${i.x}` : ` `
      };
    }
  );

  return (
    <Card title="Year" className="search-facets-facet mb-5">
      <div>
        {(searchParams.get('publication_year__lte') || searchParams.get('publication_year__gte')) && (
          <div className="text-right mb-3">
            <Button
              onClick={resetFilters}
              className="ml-1"
              type="primary"
              size="small"
            >
              Reset
            </Button>
          </div>
        )}
        <XYPlot
          height={80}
          width={150}
          margin={0}
          className="year-facet"
        >
          {hoveredBar && <Hint value={hoveredBar} />}
          <VerticalBarSeries
            className="current-data"
            color="#3498db"
            data={filters}
            onValueClick={onBarClick}
            onValueMouseOver={onBarMouseHover}
            onValueMouseOut={onBarMouseOut}
            barWidth={0.5}
          />
        </XYPlot>
      </div>
      <Slider
        range
        disabled={Object.keys(marks).length <= 1 }
        step={null}
        className="year-facet-slider"
        onChange={onSliderChange}
        onAfterChange={onSliderAfterChange}
        value={sliderEndpoints}
        defaultValue={initialEndpoints}
        min={initialEndpoints[0]}
        max={initialEndpoints[1]}
        marks={marks}
      />
    </Card>
  );
};

export default YearFacet;
