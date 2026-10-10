import type { Metadata } from "next";
import LegalPage, {
  LegalP,
  LegalList,
  LegalStrong,
  type LegalSection,
} from "@/components/legal/LegalPage";

export const metadata: Metadata = {
  title: "Cookie Policy — Novi",
  description:
    "How Novi uses cookies and similar technologies to keep the service working and improve your experience.",
};

const cookieTypes = [
  {
    purpose: "Essential cookies",
    detail:
      "Required for the Service to function — remembering your session, keeping you signed in, and remembering your theme preference.",
    storage: "Session / up to 12 months",
  },
  {
    purpose: "Preference cookies",
    detail:
      "Remember your dashboard settings, language, and saved preferences so your experience feels personal.",
    storage: "Up to 12 months",
  },
  {
    purpose: "Analytics cookies",
    detail:
      "Help us understand how visitors use Novi so we can measure performance and improve features. Data is aggregated and de-identified.",
    storage: "Up to 24 months",
  },
  {
    purpose: "Marketing cookies",
    detail:
      "Used (with your consent where required) to serve relevant content about Novi on other websites and measure campaign performance.",
    storage: "Up to 24 months",
  },
];

const sections: LegalSection[] = [
  {
    id: "what-are-cookies",
    title: "What Are Cookies",
    content: (
      <>
        <LegalP>
          Cookies are small text files placed on your device when you visit a
          website. They are widely used to make websites work, or to work more
          efficiently, and to report information to the owners of the site.
        </LegalP>
        <LegalP>
          This Cookie Policy explains what cookies and similar technologies
          (such as local storage and pixels) Novi uses, why we use them, and
          how you can control them. It supplements our{" "}
          <a
            href="/privacy"
            className="font-semibold text-primary underline-offset-4 hover:underline"
          >
            Privacy Policy
          </a>
          .
        </LegalP>
      </>
    ),
  },
  {
    id: "how-we-use-cookies",
    title: "How We Use Cookies",
    content: (
      <>
        <LegalP>We use cookies and similar technologies to:</LegalP>
        <LegalList
          items={[
            "Keep the Service running smoothly and securely — for example, keeping you signed in and remembering your theme.",
            "Understand how visitors use Novi so we can improve navigation, content, and features.",
            "Remember your preferences, such as saved roadmaps and dashboard settings.",
            "Support measurement of our marketing efforts, where you have consented.",
          ]}
        />
      </>
    ),
  },
  {
    id: "types-of-cookies",
    title: "Types of Cookies We Use",
    content: (
      <>
        <LegalP>
          The cookies we use fall into the categories below. Some are set by
          Novi directly (&quot;first-party cookies&quot;) and some are set by our trusted
          partners (&quot;third-party cookies&quot;).
        </LegalP>
        <div className="overflow-hidden rounded-2xl border border-border-soft">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="bg-background/60 text-xs uppercase tracking-widest text-muted">
                <tr>
                  <th className="px-4 py-3 font-semibold">Purpose</th>
                  <th className="px-4 py-3 font-semibold">What it does</th>
                  <th className="px-4 py-3 font-semibold">Storage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border-soft text-muted">
                {cookieTypes.map((c) => (
                  <tr key={c.purpose} className="align-top">
                    <td className="px-4 py-4 font-semibold whitespace-nowrap text-foreground">
                      {c.purpose}
                    </td>
                    <td className="px-4 py-4 leading-relaxed">{c.detail}</td>
                    <td className="px-4 py-4 whitespace-nowrap">{c.storage}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <LegalP>
          The exact cookies may change as we improve the Service. We will update
          this page when they do; significant changes will be communicated in
          line with our Privacy Policy.
        </LegalP>
      </>
    ),
  },
  {
    id: "managing-cookies",
    title: "Managing & Disabling Cookies",
    content: (
      <>
        <LegalP>
          You can control and delete cookies through your browser settings.
          Most browsers let you view stored cookies, delete them individually,
          or block them entirely.
        </LegalP>
        <LegalList
          items={[
            "Blocking or deleting essential cookies may prevent you from signing in or using parts of the Service.",
            "You can also opt out of our theme preference and analytics via your account settings where available.",
            "For blocking analytics, tools such as the browser's \"incognito\" mode or privacy extensions may help.",
          ]}
        />
        <LegalP>
          For help managing cookies, refer to the help section of your browser
          (e.g., Chrome, Safari, Firefox, or Edge).
        </LegalP>
      </>
    ),
  },
  {
    id: "third-party-cookies",
    title: "Third-Party & Analytics Cookies",
    content: (
      <>
        <LegalP>
          We work with analytics providers to understand how the Service is
          used. These providers may set their own cookies or use similar
          technologies to collect usage data on our behalf. The information is
          used in aggregate to improve Novi and is not used by us to identify
          individual users.
        </LegalP>
        <LegalP>
          Where required by law, we ask for your consent before loading
          non-essential analytics or marketing cookies, and you can change your
          choice at any time.
        </LegalP>
      </>
    ),
  },
  {
    id: "do-not-track",
    title: "Do Not Track Signals",
    content: (
      <>
        <LegalP>
          Some browsers transmit &quot;Do Not Track&quot; (DNT) signals. Because there is
          not yet a common standard for how websites should respond to these
          signals, we currently do not respond to browser DNT signals. You can
          still control most tracking through the browser and preference
          controls described in this policy.
        </LegalP>
      </>
    ),
  },
  {
    id: "changes",
    title: "Changes to This Policy",
    content: (
      <>
        <LegalP>
          We may update this Cookie Policy from time to time. We will post any
          changes on this page and update the &quot;Last updated&quot; date at the top.
          Please check this page regularly to stay informed.
        </LegalP>
      </>
    ),
  },
  {
    id: "contact",
    title: "Contact Us",
    content: (
      <>
        <LegalP>Questions about our use of cookies? Contact us at:</LegalP>
        <LegalList
          items={[
            <>
              <LegalStrong>Email:</LegalStrong> support@novi.ai
            </>,
            <>
              <LegalStrong>Subject line:</LegalStrong> &quot;Privacy&quot;
            </>,
          ]}
        />
      </>
    ),
  },
];

export default function CookiePolicyPage() {
  return (
    <LegalPage
      badge="Legal"
      headline={
        <>
          Cookies made
          <br />
          clear & simple.
        </>
      }
      intro="This Cookie Policy explains what cookies are, how Novi uses them to keep the service working, remember your preferences, and understand how you use the platform."
      lastUpdated="September 13, 2026"
      sections={sections}
    />
  );
}