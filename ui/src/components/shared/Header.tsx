/* eslint-disable react/jsx-key */
import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "antd";
import { MenuOutlined } from "@ant-design/icons";

import { MenuItem } from "@/types";
import { BASE_URL } from "@/utils/utils";

interface MenuProps {
  items: MenuItem[];
  mobile?: boolean;
  collapsed?: boolean;
}

const labels = [
  <Link href="/">Home</Link>,
  <Link href="https://scoap3.org/" target="_blank" rel="noopener noreferrer">
    Scoap³ project
  </Link>,
  <Link href="/partners">Partners</Link>,
  <a
    href="https://scoap3.org/scoap3-repository"
    target="_blank"
    rel="noopener noreferrer"
  >
    About
  </a>,
  <a
    href="https://scoap3.org/scoap3-repository-help"
    target="_blank"
    rel="noopener noreferrer"
  >
    Help
  </a>,
  <a
    href="https://github.com/SCOAP3/scoap3-next/wiki"
    target="_blank"
    rel="noopener noreferrer"
  >
    Documentation
  </a>,
  <a href={`${BASE_URL}/admin/login`} target="_blank" rel="noopener noreferrer">
    Login
  </a>,
];

const Menu: React.FC<MenuProps> = ({
  items,
  mobile = false,
  collapsed = true,
}) => (
  <ul
    className={`menu-${mobile ? "mobile" : "desktop"} ant-menu ${
      collapsed ? "collapsed" : "visible"
    }`}
  >
    {items.map((item: MenuItem) => (
      <li className="ant-menu-item" key={item.key}>
        {item.label}
      </li>
    ))}
  </ul>
);

const Header: React.FC = () => {
  const [collapsed, setCollapsed] = useState<boolean>(true);

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

  const headerItems: MenuItem[] = labels.map((label, index) => ({
    key: (index + 1).toString(),
    label,
  }));

  return (
    <div className="header">
      <div className="container flex items-center ">
        <Link className="logo" href="/">
          <Image
            src="/images/logo.png"
            width={140}
            height={40}
            alt="Logo of Scope3"
          />
        </Link>
        <Menu items={headerItems} />
        <Button onClick={toggleCollapsed}>{<MenuOutlined />}</Button>
      </div>
      <Menu mobile items={headerItems} collapsed={collapsed} />
    </div>
  );
};

export default Header;
