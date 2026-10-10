"use client";
import Gate from "../../../src/Gate";
import CheckinPage from "../../../src/views/CheckinPage";

export default function Page() {
  return <Gate page="checkin"><CheckinPage /></Gate>;
}