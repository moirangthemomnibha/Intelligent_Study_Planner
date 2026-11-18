import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { PlannerProvider } from "./context/PlannerContext";
import "./styles/index.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <PlannerProvider>
      <App />
    </PlannerProvider>
  </React.StrictMode>
);