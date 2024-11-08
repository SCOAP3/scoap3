import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Input } from "antd";
import { getSearchUrl } from "@/utils/utils";

interface SearchBarProps {
  placeholder?: string;
  hide?: boolean;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "Search",
  hide = false,
  className,
}) => {
  const router = useRouter();
  // const value = useSearchParams().get("search") ?? "";
  const value = useSearchParams().get("search_simple_query_string") ?? "";

  const [val, setVal] = useState(value);

  const { Search } = Input;

  return (
    <>
      {!hide && (
        <Search
          onSearch={() => router.push(getSearchUrl({...(val ? {search_simple_query_string: val} : {})} , true))}
          placeholder={placeholder}
          enterButton
          className={className}
          value={val}
          onChange={(e) => setVal(e?.target?.value)}
        />
      )}
    </>
  );
};

export default SearchBar;
