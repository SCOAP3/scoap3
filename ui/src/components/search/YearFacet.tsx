import React, { useEffect, useState } from "react";
import { XYPlot, VerticalBarSeries, Hint } from "react-vis";
import { Button, Card, Slider } from "antd";
import { SliderMarks } from "antd/es/slider";
import { useRouter } from "next/navigation";
import isEqual from "lodash.isequal";
import "react-vis/dist/style.css";

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
  const [shouldPush, setShouldPush] = useState<boolean>(
    !!params.publication_year__range
  );
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
    if (shouldPush) {
      router.push(
        getSearchUrl({
          ...params,
          page: 1,
          publication_year__range: resolveYearQuery(),
        })
      );
      setShouldPush(false);
    }
  }, [filters, shouldPush]);

  const resolveYearQuery = () => {
    if (sliderEndpoints[0] === sliderEndpoints[1]) {
      return sliderEndpoints[0]?.toString();
    }
    return sliderEndpoints.join("__");
  };

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
    setSliderEndpoints(getSliderEndpoints(newFilters));
    setMarks(getMarks(newFilters));
  };

  const sliderDataToGraphData = (data: number[]) => {
    const firstIndex = initialData.findIndex(
      (item: YearFacetData) => item.x === data[0]
    );
    const lastIndex = initialData.findIndex(
      (item: YearFacetData) => item.x === data[data.length - 1]
    );
    const range = initialData.slice(firstIndex, lastIndex + 1);

    if (range.length === 1) {
      return [range, range].flat();
    }

    return range;
  };

  const onSliderChange = (data: number[]) => {
    updateStateAndMarks(sliderDataToGraphData(data));
  };

  const onSliderAfterChange = (data: number[]) => {
    setFilters(sliderDataToGraphData(data));
    setShouldPush(true);
  };

  const onBarClick = (value: YearFacetData) => {
    updateStateAndMarks([value, value]);
    setFilters([value, value]);
    setShouldPush(true);
  };

  const onBarMouseHover = (bar: YearFacetData) => {
    setHoveredBar({ [bar.x]: bar.y });
  };

  const onBarMouseOut = () => setHoveredBar(null);

  const resetFilters = () => {
    setReset(!reset);
    updateStateAndMarks(initialData);
    setFilters(initialData);
    setShouldPush(true);
  };

  return (
    <Card title="Year" className="search-facets-facet mb-5">
      <div>
        {!isEqual(initialData, filters) && (
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
        <XYPlot height={80} width={150} margin={0} className="year-facet">
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
        className="year-facet-slider"
        onChange={onSliderChange}
        onAfterChange={onSliderAfterChange}
        value={sliderEndpoints}
        min={initialEndpoints[0]}
        max={initialEndpoints[1]}
        marks={marks}
      />
    </Card>
  );
};

export default YearFacet;
