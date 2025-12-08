import React from 'react';

const Footer = () => (
  <footer style={{
    marginTop: '32px',
    padding: '24px',
    backgroundColor: '#0d0d0f',
    color: '#f0f0f0',
    display: 'flex',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '12px',
    borderTop: '1px solid #202027'
  }}>
    <div>© MovieHub, 2025</div>
    <div style={{display: 'flex', gap: '16px'}}>
      <a href="/static/html/auth.html" style={{color: '#f0f0f0'}}>Вход</a>
      <a href="/static/html/register.html" style={{color: '#f0f0f0'}}>Регистрация</a>
      <a href="/api/docs" style={{color: '#f0f0f0'}}>API docs</a>
    </div>
  </footer>
);

export default Footer;
