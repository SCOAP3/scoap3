import React, { useEffect, useState } from "react";
import { FlexibleWidthXYPlot, VerticalBarSeries, Hint } from "react-vis";
import 'react-vis/dist/style.css';
import { Button, Card, Slider } from "antd";
import { SliderMarks } from "antd/es/slider";
import { useRouter } from "next/navigation";
import isEqual from "lodash.isequal";

import { getSearchUrl } from "@/utils/utils";
import { PublicationYear, YearFacetData, Params } from "@/types";

interface YearFacetProps {
  data: PublicationYear[];
  params: Params;
}

const YearFacet: React.FC<YearFacetProps> = ({ data, params }) => {
  const [hoveredBar, setHoveredBar] = useState<any>(null);
  const [filters, setFilters] = useState<YearFacetData[]>([]);
  const [initialData, setInitialData] = useState<YearFacetData[]>([]);
  const [initialEndpoints, setInitialEndpoints] = useState<number[]>([]);
  const [sliderEndpoints, setSliderEndpoints] = useState<number[]>([]);
  const [marks, setMarks] = useState<SliderMarks>(undefined);
  const [reset, setReset] = useState<boolean>(false);
  const router = useRouter();

  useEffect(() => {
    const initialData = mapInitialDataToYears(data);
    setFilters(initialData);
    setInitialData(initialData);
    setSliderEndpoints(getSliderEndpoints(initialData));
    setInitialEndpoints(getSliderEndpoints(initialData));
    setMarks(getMarks(initialData));
  }, []);

  useEffect(() => {
    router.push(
      getSearchUrl({
        ...params,
        page: 1,
        publication_year__range: sliderEndpoints.join("__"),
      })
    );
  }, [filters]);

  const mapInitialDataToYears = (
    initial: PublicationYear[]
  ): YearFacetData[] => {
    return initial?.map((item) => ({
      x: new Date(item?.key)?.getFullYear(),
      y: item?.doc_count,
    }));
  };

  const getSliderEndpoints = (initial: YearFacetData[]): number[] => {
    if (initial.length === 1) return [initial[0]?.x];
    return [initial[0]?.x, initial[initial.length - 1]?.x];
  };

  const getMarks = (initial: YearFacetData[]): SliderMarks => {
    if (initial.length === 1) {
      return {
        [initial[0]?.x]: [initial[0]?.x],
      };
    }
    return {
      [initial[0]?.x]: [initial[0]?.x],
      [initial[initial.length - 1]?.x]: [initial[initial.length - 1]?.x],
    };
  };

  const updateStateAndMarks = (newFilters: YearFacetData[]) => {
    setFilters(newFilters);
    setSliderEndpoints(getSliderEndpoints(newFilters));
    setMarks(getMarks(newFilters));
  };

  const onBarClick = (value: YearFacetData) => {
    updateStateAndMarks([value]);
  };

  const onSliderChange = (data: number[]) => {
    const firstIndex = initialData.findIndex(
      (item: YearFacetData) => item.x === data[0]
    );
    const lastIndex = initialData.findIndex(
      (item: YearFacetData) => item.x === data[data.length - 1]
    );
    const range = initialData.slice(firstIndex, lastIndex + 1);

    updateStateAndMarks(range);
  };

  const onBarMouseHover = (bar: YearFacetData) => {
    setHoveredBar({ [bar.x]: bar.y });
  };

  const onBarMouseOut = () => setHoveredBar(null);

  const resetFilters = () => {
    setReset(!reset);
    updateStateAndMarks(initialData);
  };

  return (
    <Card title="Year" className="search-facets-facet mb-5">
      <div>
        {!isEqual(initialData, filters) && (
          <div className="text-right">
            <Button onClick={resetFilters} className="ml-1" type="primary" size="small">
              Reset
            </Button>
          </div>
        )}
        <FlexibleWidthXYPlot
          height={80}
          width={150}
          margin={0}
          className="year-facet"
        >
          <VerticalBarSeries
            className="pointer"
            color="#3498db"
            barWidth={0.6}
            data={filters}
            onValueClick={onBarClick}
            onValueMouseOver={onBarMouseHover}
            onValueMouseOut={onBarMouseOut}
          />
          {hoveredBar && <Hint value={hoveredBar} />}
        </FlexibleWidthXYPlot>
      </div>
      <Slider
        range
        className="year-facet-slider"
        onChange={onSliderChange}
        value={sliderEndpoints}
        min={initialEndpoints[0]}
        max={initialEndpoints[1]}
        marks={marks}
      />
    </Card>
  );
};

export default YearFacet;
