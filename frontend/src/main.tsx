import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Theme } from "@radix-ui/themes";
import App from "./App";
import { AuthProvider } from "./auth";
// Only the color scales the app uses (lime/gray theme + red/green/amber tones)
// instead of styles.css, which ships all 30 scales.
import "@radix-ui/themes/tokens/base.css";
import "@radix-ui/themes/tokens/colors/lime.css";
import "@radix-ui/themes/tokens/colors/gray.css";
import "@radix-ui/themes/tokens/colors/red.css";
import "@radix-ui/themes/tokens/colors/green.css";
import "@radix-ui/themes/tokens/colors/amber.css";
import "@radix-ui/themes/components.css";
import "@radix-ui/themes/utilities.css";
import "./radix-theme.css"; // must follow the Radix stylesheet
import "./index.css";

// ponytail: dark only, matching the Radix custom-palette preview. The light
// scales are still generated in radix-theme.css; add a toggle if users ask.
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Theme appearance="dark" accentColor="lime" grayColor="gray" radius="medium" scaling="110%">
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </Theme>
  </React.StrictMode>
);
