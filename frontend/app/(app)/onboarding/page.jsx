"use client";
import Gate from "../../../src/Gate";
import OnboardingPage from "../../../src/views/OnboardingPage";

// The live onboarding engine is the single 15-step flow + voice engine
// (app/routers/onboarding.py), served at /onboarding/flow/* with /onboarding/voice/*.
// The legacy engine was removed; OnboardingPage is the only onboarding UI.
export default function Page() {
  return <Gate page="onboarding"><OnboardingPage /></Gate>;
}