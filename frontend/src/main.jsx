import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import "./index.css";

import App from "./App.jsx";
import Home from "./pages/Home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import MatchHistory from "./pages/MatchHistory.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route path="/" element={<Home />} />

        <Route
          path="/resumes/:resumeId/matches"
          element={<MatchHistory />}
        />

        <Route
          path="/matches/:matchId"
          element={<App />}
        />
      </Routes>
    </BrowserRouter>
  </StrictMode>
);