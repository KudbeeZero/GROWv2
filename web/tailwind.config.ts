import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        grow: {
          50: "#f1fae9",
          100: "#dcf3c4",
          200: "#bde88c",
          300: "#97d84f",
          400: "#76c024",
          500: "#5aa015",
          600: "#447d0f",
          700: "#356010",
          800: "#2c4c13",
          900: "#274014",
        },
        ink: {
          900: "#0d1117",
          800: "#161b22",
          700: "#21262d",
          600: "#30363d",
          500: "#484f58",
        },
      },
    },
  },
  plugins: [],
};

export default config;
