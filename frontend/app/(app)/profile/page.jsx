"use client";
import Gate from "../../../src/Gate";
import ProfilePage from "../../../src/views/ProfilePage";

export default function Page() {
  return <Gate page="profile"><ProfilePage /></Gate>;
}