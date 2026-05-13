import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // On page load, check if user is saved in local storage
  useEffect(() => {
    const savedUser = localStorage.getItem('gymUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // Login function called from the Login page
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem('gymUser', JSON.stringify(userData));
  };

  // Logout function called from the Navbar
  const logout = () => {
    setUser(null);
    localStorage.removeItem('gymUser');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
