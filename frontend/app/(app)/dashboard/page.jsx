"use client";
import Gate from "../../../src/Gate";
import DashboardPage from "../../../src/views/DashboardPage";

export default function Page() {
  return <Gate page="dashboard"><DashboardPage /></Gate>;
}