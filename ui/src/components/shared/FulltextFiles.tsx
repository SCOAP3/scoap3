import React from "react";
import { FilePdfOutlined, FileTextOutlined } from "@ant-design/icons";

import { Extension, File, supportedExtensions } from "@/types";

const isSupportedExtension = (
  value: string | undefined
): value is Extension => {
  return supportedExtensions.includes(value as Extension);
};

const formatsWithIcons: Record<
  Extension,
  { label: string; icon: JSX.Element }
> = {
  pdf: {
    label: " PDF",
    icon: <FilePdfOutlined />,
  },
  pdfa: {
    label: " PDF/A",
    icon: <FilePdfOutlined />,
  },
  xml: {
    label: " XML",
    icon: <FileTextOutlined />,
  },
};

type FulltextFilesProps = {
  files: File[];
  size?: "small" | "big";
};

const FulltextFiles: React.FC<FulltextFilesProps> = ({
  files,
  size = "big",
}) => {
  const fileExtensionRegex = /(?:\.([^.]+))?$/;

  return (
    <>
      {files?.map((file) => {
        let fileExtension = fileExtensionRegex.exec(file?.file)?.[1];

        if (
          file?.file?.slice(-6, -4) === "_a" ||
          file?.file?.slice(-6, -4) === ".a"
        ) {
          fileExtension = "pdfa";
        }

        if (isSupportedExtension(fileExtension)) {
          const { icon, label } = formatsWithIcons[fileExtension];
          return (
            <a
              key={file?.file}
              href={file?.file}
              className={`file-${size} mr-2`}
              target="_blank"
              rel="noopener noreferrer"
            >
              {icon}
              {label}
            </a>
          );
        }

        return null;
      })}
    </>
  );
};

export default FulltextFiles;
