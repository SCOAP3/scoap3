import React from "react";
import Footer from "./Footer";
import Header from "./Header";
import { UserProvider } from "@/components/shared/UserContext";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <UserProvider>
      <div className="app flex flex-col justify-between">
        <Header />
        <main>{children}</main>
        <Footer />
      </div>
    </UserProvider>
  );
};

export default Layout;
