import type { Metadata } from "next";
import LegalPage, {
  LegalP,
  LegalList,
  LegalStrong,
  type LegalSection,
} from "@/components/legal/LegalPage";

export const metadata: Metadata = {
  title: "Privacy Policy — Novi",
  description:
    "How Novi collects, uses, and protects your personal information.",
};

const sections: LegalSection[] = [
  {
    id: "introduction",
    title: "Introduction",
    content: (
      <>
        <LegalP>
          <LegalStrong>Novi</LegalStrong> (&quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) is an
          AI-powered platform that helps students from Grade 9 through
          university discover careers, explore universities, and build
          personalized roadmaps to their goals. This Privacy Policy explains
          what information we collect when you visit our website or use our
          services (together, the &quot;Service&quot;), how we use it, and the choices
          you have.
        </LegalP>
        <LegalP>
          By accessing or using the Service, you agree to the collection, use,
          and sharing of information as described in this policy. If you do not
          agree, please do not use the Service.
        </LegalP>
      </>
    ),
  },
  {
    id: "information-we-collect",
    title: "Information We Collect",
    content: (
      <>
        <LegalP>
          We collect information you provide directly, information we collect
          automatically as you use the Service, and information from
          third-party sources. We collect this information to provide, improve,
          and personalize Novi.
        </LegalP>
        <LegalList
          items={[
            <>
              <LegalStrong>Account information.</LegalStrong> Your name, email
              address, password, grade level, and school when you create an
              account or join our waitlist.
            </>,
            <>
              <LegalStrong>Profile and goal data.</LegalStrong> Details you
              share about your interests, strengths, career aspirations,
              university preferences, and progress — including the results of
              assessment quizzes and career &quot;DNA&quot; profiling.
            </>,
            <>
              <LegalStrong>Parent information.</LegalStrong> If you create a
              parent account, we collect your name, email address, and the
              profile information linked to your student so we can provide
              dashboards and progress insights.
            </>,
            <>
              <LegalStrong>AI mentor conversations.</LegalStrong> Prompts,
              questions, and other content you submit to the Novi AI mentor, as
              well as the responses we generate.
            </>,
            <>
              <LegalStrong>Usage data.</LegalStrong> Pages you visit, features
              you use, time spent, and interactions such as clicks and
              roadmaps completed.
            </>,
            <>
              <LegalStrong>Device and technical data.</LegalStrong> IP address,
              browser type, operating system, device identifiers, and
              approximate location (down to city level).
            </>,
          ]}
        />
      </>
    ),
  },
  {
    id: "how-we-use-your-information",
    title: "How We Use Your Information",
    content: (
      <>
        <LegalP>
          We use the information we collect to operate and improve the
          Service. Specifically, we use it to:
        </LegalP>
        <LegalList
          items={[
            "Create and manage your account, and authenticate you when you sign in.",
            "Run the Novi AI mentor, personalize career and university recommendations, and generate roadmaps tailored to you or your student.",
            "Provide parent dashboards and progress insights for connected accounts.",
            "Improve our AI models, features, and content.",
            "Send you service updates, product announcements, and (with your consent) marketing communications.",
            "Prevent abuse, fraud, and unauthorized access, and maintain the security of the Service.",
            "Comply with legal obligations and enforce our Terms of Service.",
          ]}
        />
      </>
    ),
  },
  {
    id: "ai-mentor-and-student-content",
    title: "AI Mentor & Student Content",
    content: (
      <>
        <LegalP>
          Conversations with the Novi AI mentor are used to generate responses
          and to personalize your experience. When you submit content — such as
          a question, journal entry, or goal — we process that content to
          produce guidance and recommendations.
        </LegalP>
        <LegalP>
          Your conversations and profile data are treated as confidential and
          are only used to power your personal experience and to improve our
          service in an anonymized or aggregated form. We do not use student
          conversation content to market to you without your permission. If you
          delete your account, we delete or de-identify this content as
          described in the Data Retention section below, subject to legal
          retention requirements.
        </LegalP>
      </>
    ),
  },
  {
    id: "how-we-share",
    title: "How We Share Information",
    content: (
      <>
        <LegalP>
          We do not sell your personal information. We share information only
          in the circumstances described below:
        </LegalP>
        <LegalList
          items={[
            <>
              <LegalStrong>Service providers.</LegalStrong> Trusted vendors
              that help us operate the Service (hosting, analytics, customer
              support, email delivery, and AI infrastructure). They process
              data only on our behalf and under contractual restrictions.
            </>,
            <>
              <LegalStrong>Universities and partners.</LegalStrong> If your
              school, counselor, or a university program you enroll through
              integrates with Novi, we may share relevant information with them
              at your direction or with your consent.
            </>,
            <>
              <LegalStrong>Parents and guardians.</LegalStrong> If a parent
              account is connected to your student account, we share progress
              and dashboard information with that parent.
            </>,
            <>
              <LegalStrong>Legal compliance.</LegalStrong> When required by
              law, regulation, or legal process, or to protect the rights,
              safety, and property of Novi, our users, or the public.
            </>,
            <>
              <LegalStrong>Business transfers.</LegalStrong> In connection with
              a merger, sale, or acquisition, your information may be
              transferred as part of that transaction.
            </>,
          ]}
        />
      </>
    ),
  },
  {
    id: "data-security",
    title: "Data Security",
    content: (
      <>
        <LegalP>
          We take reasonable administrative, technical, and physical measures
          to protect your information from unauthorized access, loss,
          misuse, or alteration. These include encryption of data in transit
          and at rest, least-privilege access controls, regular security
          reviews, and staff training.
        </LegalP>
        <LegalP>
          No method of transmission over the Internet or method of electronic
          storage is 100% secure. While we work hard to protect your
          information, we cannot guarantee its absolute security. You can help
          by choosing a strong password and keeping your login credentials
          private.
        </LegalP>
      </>
    ),
  },
  {
    id: "data-retention",
    title: "Data Retention",
    content: (
      <>
        <LegalP>
          We retain your information only as long as necessary to provide the
          Service, comply with our legal obligations, resolve disputes, and
          enforce our agreements. In general:
        </LegalP>
        <LegalList
          items={[
            "Account and profile data are kept while your account is active.",
            "AI mentor conversations are retained to keep your experience continuous; you or your parent can request deletion at any time.",
            "Aggregated, de-identified analytics may be retained for longer periods for research and product improvement.",
          ]}
        />
        <LegalP>
          When you delete your account, we initiate deletion or
          de-identification of your personal data within a reasonable time,
          unless we are legally required to retain it.
        </LegalP>
      </>
    ),
  },
  {
    id: "childrens-privacy",
    title: "Children's Privacy",
    content: (
      <>
        <LegalP>
          Novi is designed for students in secondary education. We do not
          knowingly collect personal information from children under the age of
          13 without verifiable parental consent. Where local law sets a higher
          age for consent (for example, 16 in parts of the European Economic
          Area), we comply with that law.
        </LegalP>
        <LegalP>
          If you are a parent or guardian and believe your child has provided
          us with personal information without your consent, please contact us
          using the details below and we will take steps to remove that
          information. For schools and districts handling student records, we
          comply with applicable student privacy laws, including FERPA where
          applicable.
        </LegalP>
      </>
    ),
  },
  {
    id: "your-rights-and-choices",
    title: "Your Rights & Choices",
    content: (
      <>
        <LegalP>
          Depending on where you live, you may have the right to access,
          correct, delete, or obtain a copy of your personal information, to
          restrict or object to certain processing, and to withdraw consent at
          any time. You may also have the right to complain to a supervisory
          authority.
        </LegalP>
        <LegalList
          items={[
            <>
              <LegalStrong>Account settings.</LegalStrong> You can review and
              update your profile and preferences from your account dashboard.
            </>,
            <>
              <LegalStrong>Email preferences.</LegalStrong> You can opt out of
              marketing emails at any time using the unsubscribe link in any
              message.
            </>,
            <>
              <LegalStrong>Access and deletion.</LegalStrong> You can request a
              copy of your data or ask us to delete it by contacting us below.
            </>,
            <>
              <LegalStrong>Cookie controls.</LegalStrong> You can manage
              tracking and analytics cookies through your browser and our
              Cookie Policy.
            </>,
          ]}
        />
      </>
    ),
  },
  {
    id: "international-transfers",
    title: "International Data Transfers",
    content: (
      <>
        <LegalP>
          We are based in the United States and may transfer, store, and
          process your information in countries outside your country of
          residence. When we transfer personal data internationally, we use
          appropriate safeguards — such as standard contractual clauses or
          equivalent mechanisms — to help ensure your information receives an
          equivalent level of protection.
        </LegalP>
      </>
    ),
  },
  {
    id: "third-party-links",
    title: "Third-Party Links & Services",
    content: (
      <>
        <LegalP>
          Our Service may contain links to third-party websites, tools, or
          services (such as university portals or career resources). This
          Privacy Policy does not apply to those third parties. We encourage
          you to review the privacy policies of any third-party service you
          use.
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
          We may update this Privacy Policy from time to time to reflect
          changes in our practices, technology, or legal requirements. When we
          make material changes, we will notify you by updating the &quot;Last
          updated&quot; date at the top of this page and, where appropriate, by
          email or an in-product notice. Your continued use of the Service
          after changes are posted constitutes acceptance of the revised
          policy.
        </LegalP>
      </>
    ),
  },
  {
    id: "contact-us",
    title: "Contact Us",
    content: (
      <>
        <LegalP>
          If you have questions, concerns, or requests about this Privacy
          Policy or our data practices, please contact us at:
        </LegalP>
        <LegalList
          items={[
            <>
              <LegalStrong>Email:</LegalStrong> support@novi.ai
            </>,
            <>
              <LegalStrong>Subject line:</LegalStrong> &quot;Privacy&quot; — this helps
              us route your request to the right team.
            </>,
          ]}
        />
        <LegalP>
          We aim to respond to privacy requests within a reasonable time, and
          no later than 30 days, where required by law.
        </LegalP>
      </>
    ),
  },
];

export default function PrivacyPolicyPage() {
  return (
    <LegalPage
      badge="Legal"
      headline={
        <>
          Your privacy matters.
          <br />
          Always.
        </>
      }
      intro="This Privacy Policy explains how Novi collects, uses, protects, and shares your personal information when you use our AI mentor, career and university explorers, roadmaps, and related services."
      lastUpdated="September 13, 2026"
      sections={sections}
    />
  );
}