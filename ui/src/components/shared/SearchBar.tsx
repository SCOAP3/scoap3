import React, { useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { Input } from "antd";

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
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const value = searchParams.get("search_simple_query_string") ?? "";

  const [val, setVal] = useState(value);

  const { Search } = Input;

  useEffect(() => {
    setVal(value)

  }, [value])

  return (
    <>
      {!hide && (
        <Search
          onSearch={(value, event, { source = "input" } = {}) => {

            const params = new URLSearchParams(searchParams.toString());

            if (source === "clear") {
              params.delete("search_simple_query_string")
            }
            else {
              if (val) params.set("search_simple_query_string", val);
              else params.delete("search_simple_query_string")
            }
            router.push("/search" + (params.toString() ? `?${params.toString()}` : ""))
          }}
          placeholder={placeholder}
          enterButton
          className={className}
          value={val}
          onChange={(e) => setVal(e?.target?.value)}
          allowClear={pathname == "/search"}
        />
      )}
    </>
  );
};

export default SearchBar;
