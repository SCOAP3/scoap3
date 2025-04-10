/* eslint-disable react/jsx-key */
import React, { MouseEventHandler, useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { Button } from "antd";
import { MenuOutlined } from "@ant-design/icons";

import { MenuItem } from "@/types";
import { BASE_URL } from "@/utils/utils";

interface MenuProps {
  items: MenuItem[];
  onClick?: MouseEventHandler<HTMLLIElement>;
  mobile?: boolean;
  collapsed?: boolean;
}

const Menu: React.FC<MenuProps> = ({
  items,
  onClick = () => {},
  mobile = false,
  collapsed = true,
}) => (
  <ul
    className={`menu-${mobile ? "mobile" : "desktop"} ant-menu ${
      collapsed ? "collapsed" : "visible"
    }`}
  >
    {items.map((item: MenuItem) => (
      <li className="ant-menu-item" key={item.key} onClick={onClick}>
        {item.label}
      </li>
    ))}
  </ul>
);

const Header: React.FC = () => {
  const [collapsed, setCollapsed] = useState<boolean>(true);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);

  const toggleCollapsed = () => {
    setCollapsed(!collapsed);
  };

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const res = await fetch(`${BASE_URL}/api/users/me/`, {
          method: "GET",
          credentials: "include",
        });
        if (res.status === 200) {
          setIsLoggedIn(true);
        } else {
          setIsLoggedIn(false);
        }
      } catch (error) {
        console.error("Error checking login:", error);
      }
    };

    checkLoginStatus();

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        checkLoginStatus();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  const labels = [
    <Link href="/">Home</Link>,
    <Link href="https://scoap3.org/" target="_blank" rel="noopener noreferrer">
      SCOAP3 project
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
      href="https://github.com/SCOAP3/scoap3/wiki"
      target="_blank"
      rel="noopener noreferrer"
    >
      Documentation
    </a>,
    isLoggedIn ? (
      <a href={`${BASE_URL}/admin/logout`} target="_blank" rel="noopener noreferrer">Log out</a>
    ) : (
      <a href={`${BASE_URL}/admin/login`} target="_blank" rel="noopener noreferrer">Login</a>
    ),
  ];

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
      <Menu
        mobile
        items={headerItems}
        collapsed={collapsed}
        onClick={toggleCollapsed}
      />
    </div>
  );
};

export default Header;
