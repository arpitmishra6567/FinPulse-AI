import type { Config } from "tailwindcss";
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: { extend: { colors: { brand: { DEFAULT: "#0f4c81", dark: "#0b3a63" } } } },
  plugins: [],
} satisfies Config;