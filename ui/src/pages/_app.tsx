import React from "react";
import { ConfigProvider } from "antd";
import Head from "next/head";
import NextNProgress from "nextjs-progressbar";
import { PT_Sans_Narrow } from "next/font/google";

import "@/styles/globals.css";
import theme from "../theme/themeConfig";
import Layout from "@/components/shared/Layout";

interface AppProps {
  Component: any;
  pageProps: any;
}

const font = PT_Sans_Narrow({
  weight: ["400", "700"],
  style: ["normal"],
  subsets: ["latin"],
  display: "swap",
});

const App: React.FC<AppProps> = ({ Component, pageProps }) => (
  <ConfigProvider theme={theme}>
    <style jsx global>{`
      html {
        font-family: ${font.style.fontFamily};
      }
    `}</style>
    <Layout>
      <Head>
        <title>SCOAP3 Repository</title>
      </Head>
      <NextNProgress />
      <Component {...pageProps} />
    </Layout>
  </ConfigProvider>
);

export default App;
