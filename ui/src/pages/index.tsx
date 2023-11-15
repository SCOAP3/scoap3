import React from "react";
import { Tabs } from "antd";
import Image from "next/image";
import { GetServerSideProps } from "next";

import TabContent from "@/components/home/TabContent";
import SearchBar from "@/components/shared/SearchBar";
import { Journal, Country, Facets, Response, Params } from "@/types";
import { authToken, getApiUrl, getSearchUrl } from "@/utils/utils";

interface HomePageProps {
  count: number;
  facets: Facets;
  query: Params;
}

const HomePage: React.FC<HomePageProps> = ({ count, facets, query }) => {
  const journals: Journal[] = facets?._filter_journal?.journal?.buckets;
  const partners: Country[] = facets?._filter_country?.country?.buckets;

  const tabItems = [
    {
      key: "1",
      label: "Journals",
      children: <TabContent data={journals} type="journal" />,
    },
    {
      key: "2",
      label: "SCOAP3 partners",
      children: <TabContent data={partners} type="country" />,
    },
  ];

  return (
    <>
      <Image
        width={0}
        height={0}
        sizes="100vw"
        src="/images/background.jpeg"
        alt="Background picture of Scope3"
        className="banner"
        priority
      />
      <div className="container">
        <div className="container-inner">
          <p className="text-center mb-4">
            Search <b>{count} Open Access</b> articles:
          </p>
          <SearchBar
            placeholder="Type and press enter to search"
            className="home-searchbar mb-6"
          />
          <Tabs type="card" items={tabItems} />
        </div>
      </div>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async () => {
  const query = { search: "" };

  const res = await fetch(`${getApiUrl() + getSearchUrl(query)}`, authToken);
  const { count, facets } = (await res?.json()) as Response;

  return { props: { count, facets, query } };
};

export default HomePage;
