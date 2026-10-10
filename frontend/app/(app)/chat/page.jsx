"use client";
import Gate from "../../../src/Gate";
import ChatPage from "../../../src/views/ChatPage";

export default function Page() {
  return <Gate page="chat"><ChatPage /></Gate>;
}