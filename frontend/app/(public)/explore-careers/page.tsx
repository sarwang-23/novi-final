import type { Metadata } from "next";
import NavBar from "@/components/ui/NavBar";
import CareersHero from "@/components/careers/CareersHero";
import CareersJourney from "@/components/careers/CareersJourney";
import CareersAIMatching from "@/components/careers/CareersAIMatching";
import CareersSocialProof from "@/components/careers/CareersSocialProof";
import CareersCTAFooter from "@/components/careers/CareersCTAFooter";

export const metadata: Metadata = {
  title: "Career Discovery — What Could You Become?",
  description:
    "There are thousands of careers you've probably never heard of. Novi helps you discover the ones that could be right for you — based on who you are.",
};

export default function CareersPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background text-foreground">
      <NavBar />
      <main className="relative z-10 flex flex-col">
        <CareersHero />
        <CareersJourney />
        <CareersAIMatching />
        <CareersSocialProof />
        <CareersCTAFooter />
      </main>
    </div>
  );
}