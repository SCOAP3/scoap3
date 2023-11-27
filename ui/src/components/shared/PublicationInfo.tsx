import React from "react";
import ReactHtmlParser from "react-html-parser";

import { JournalInfo } from "@/types";

interface PublicationInfoProps {
  data: JournalInfo;
  page: "search" | "detail";
}

const PublicationInfo: React.FC<PublicationInfoProps> = ({ data, page }) => {
  const {
    journal_title,
    journal_volume,
    journal_issue,
    volume_year,
    page_start,
    page_end,
    publisher,
  } = data || {};

  let publicationText = "";

  if (journal_title) {
    publicationText += `<span class="publication-info-title">${journal_title}</span>`;
  }

  if (journal_volume) {
    publicationText += `<span class="publication-info-volume">, Volume ${journal_volume}</span>`;
  }

  if (volume_year) {
    publicationText += `<span class="publication-info-volume_year"> (${volume_year})</span>`;
  }

  if (journal_issue) {
    publicationText += `<span class="publication-info-issue"> Issue ${journal_issue.replace(
      /^0+/,
      ""
    )}</span>`;
  }

  if (page_start && page === "search") {
    publicationText += " (";
  }

  if (page_start) {
    publicationText += `<span class="publication-info-pages">Page${
      page_end ? "s" : ""
    } ${page_start.toString().replace(/^0+/, "")}${
      page_end ? `-${+page_end.toString().replace(/^0+/, "")}` : ""
    }</span>`;
  }

  if (page_start && page === "search") {
    publicationText += ")";
  }

  if (page === "search" && publisher) {
    const publisherBold = `<b>${publisher}</b>`;
    publicationText += ` by ${publisherBold}`;
  }

  return (
    <p
      className={`publication-info-${page} ${
        page === "search" && "text-sm"
      } inline-block mb-1`}
    >
      {ReactHtmlParser(publicationText)}
    </p>
  );
};

export default PublicationInfo;
