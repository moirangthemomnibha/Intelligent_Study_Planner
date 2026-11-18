import { createContext, useContext, useState } from "react";
const AuthContext = createContext(null);
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Add signup/signin/logout and secure token lifecycle after backend auth exists.
  return <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
