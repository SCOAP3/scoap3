import React from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "antd";
import { ClearOutlined } from "@ant-design/icons";

interface ResetSearchButtonProps {
  className?: string;
}

const ResetSearchButton: React.FC<ResetSearchButtonProps> = ({ className }) => {
  const router = useRouter();
  const searchParams = useSearchParams();

  const hasSearchParams = searchParams.toString().length > 0;

  const handleReset = () => {
    router.push('/search');
  };

  if (!hasSearchParams) {
    return null;
  }

  return (
    <Button
      onClick={handleReset}
      icon={<ClearOutlined />}
      className={className}
      type="default"
    >
      Reset Search
    </Button>
  );
};

export default ResetSearchButton;
