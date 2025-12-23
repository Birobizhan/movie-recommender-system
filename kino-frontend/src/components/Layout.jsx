import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Footer from './Footer';

const Layout = () => {
  return (
    <>
      {/* Шапка сайта */}
      <Header />
      <Outlet />
      
      {/* Подвал сайта */}
      <Footer />
    </>
  );
};

export default Layout;