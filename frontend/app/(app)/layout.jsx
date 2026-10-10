import AppShell from "../../src/Shell";
import "../../static/styles.css";
import "../../src/views/planner/planner.css";
import "../../src/views/checkin.css";

export default function AppLayout({ children }) {
  return <AppShell>{children}</AppShell>;
}