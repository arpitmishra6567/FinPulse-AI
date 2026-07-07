import type { Metadata } from "next";
import "./globals.css";
import Shell from "@/components/shell";

export const metadata: Metadata = {
  title: "FinPulse AI — Financial Health Intelligence",
  description: "Explainable financial-health identity for credit-invisible MSMEs. IDBI Innovate 2026 prototype.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body><Shell>{children}</Shell></body>
    </html>
  );
}