import type { Metadata } from "next";
import ThemeProvider from "@/components/ui/ThemeProvider";
import "@/site/site.css";

export const metadata: Metadata = {
  title: "Novi — Your AI Mentor for Student Success",
  description:
    "Novi is the AI-powered Operating System for Student Success that guides you from Grade 9 to your dream university — and beyond.",
  openGraph: {
    title: "Novi — Your AI Mentor for Student Success",
    description:
      "Discover who you are. Explore what's possible. Build your path. Become who you want to be.",
    type: "website",
    siteName: "Novi",
  },
};

export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider>
      <div className="font-sans">{children}</div>
    </ThemeProvider>
  );
}