import React from "react";
import { createRoot } from "react-dom/client";

import App from "./App";

import { PlannerProvider } from "./context/PlannerContext";
import { ThemeProvider } from "./context/ThemeContext";

import "./styles/index.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider>
      <PlannerProvider>
        <App />
      </PlannerProvider>
    </ThemeProvider>
  </React.StrictMode>
);