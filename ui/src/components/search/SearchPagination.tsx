import React from "react";
import { Pagination } from "antd";
import { useRouter } from "next/navigation";

import { getSearchUrl } from "@/utils/utils";
import { Params } from "@/types";

interface SearchPagination {
  count: number;
  params: Params;
}

const SearchPagination: React.FC<SearchPagination> = ({ count, params }) => {
  const router = useRouter();

  const onPageChange = (page: number) => {
    router.push(getSearchUrl({ ...params, page }));
  };

  return (
    <Pagination
      size="small"
      pageSize={Number(params?.page_size) || 20}
      total={count}
      onChange={(page) => onPageChange(page)}
      showSizeChanger={false}
      current={Number(params?.page) || 1}
      hideOnSinglePage
      className="md:mb-0 mb-3"
    />
  );
};

export default SearchPagination;
