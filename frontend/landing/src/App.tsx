import { motion } from "framer-motion";
import FadingVideo from "./components/FadingVideo";
import BlurText from "./components/BlurText";
import {
  ShieldIcon,
  PlayIcon,
  ClockIcon,
  GlobeIcon,
  ScanIcon,
  AlertIcon,
  LockIcon,
} from "./components/Icons";

const HERO_VIDEO =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260619_191346_9d19d66e-86a4-47f7-8dc6-712c1788c3b2.mp4";

const CAPABILITIES_VIDEO =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260622_093722_ccfc7ebf-182f-419f-8a62-2dc02db7dd9d.mp4";

const NAV_LINKS = ["Features", "Solutions", "Pricing", "Docs", "Contact"];
const LOGOS = ["ShieldCorp", "CyberSafe", "NetGuard", "ThreatX", "SecureOps"];

const fadeIn = (delay: number) =>
  ({
    initial: { filter: "blur(10px)", opacity: 0, y: 20 },
    animate: { filter: "blur(0px)", opacity: 1, y: 0 },
    transition: { duration: 0.8, ease: "easeOut" as const, delay },
  }) as const;

function Hero() {
  return (
    <section className="relative h-screen overflow-hidden bg-[var(--color-canvas)]">
      <FadingVideo
        src={HERO_VIDEO}
        className="absolute left-1/2 top-0 -translate-x-1/2 object-cover object-top z-0 opacity-30"
        style={{ width: "120%", height: "120%" }}
      />

      <div className="relative z-10 flex flex-col h-full">
        <nav className="fixed top-4 left-0 right-0 z-50 flex items-center justify-between px-8 lg:px-16">
          <div className="flex items-center gap-2">
            <ShieldIcon className="w-8 h-8 text-[var(--color-primary)]" />
            <span className="text-xl font-semibold text-[var(--color-ink)]">Astra Shield</span>
          </div>
          <div className="hidden md:flex items-center gap-1 bg-[var(--color-surface-strong)] rounded-full px-2 py-2 border border-[var(--color-hairline)]">
            {NAV_LINKS.map((link) => (
              <a
                key={link}
                href="#"
                className="px-4 py-2 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] transition-colors rounded-full hover:bg-[var(--color-surface-soft)]"
              >
                {link}
              </a>
            ))}
            <button className="ml-2 btn-pill">
              Get Started
            </button>
          </div>
          <div className="h-12 w-12" />
        </nav>

        <div className="flex-1 flex flex-col items-center justify-center pt-24 px-4 text-center">
          <motion.div
            {...fadeIn(0.4)}
            className="rounded-full px-4 py-1.5 inline-flex items-center gap-2 bg-[var(--color-surface-strong)] border border-[var(--color-hairline)]"
          >
            <span className="bg-[var(--color-primary)] text-white text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
              New
            </span>
            <span className="text-xs text-[var(--color-muted)] font-light">
              AI-Powered Threat Detection — Now Available
            </span>
          </motion.div>

          <div className="mt-6 max-w-3xl">
            <BlurText
              text="Enterprise Security Built for the Modern Threat Landscape"
              className="text-6xl md:text-7xl lg:text-[5.5rem] font-semibold text-[var(--color-ink)] leading-[0.9] tracking-[-2px]"
            />
          </div>

          <motion.p
            {...fadeIn(0.8)}
            className="mt-4 text-sm md:text-base text-[var(--color-body)] max-w-2xl font-light leading-tight"
          >
            Detect phishing, scam calls, and cyber threats in real-time with our
            AI-powered platform. Protect your organization with advanced threat
            intelligence and automated response systems.
          </motion.p>

          <motion.div
            {...fadeIn(1.1)}
            className="mt-6 flex items-center gap-6"
          >
            <button className="btn-primary">
              Start Free Trial
            </button>
            <button className="flex items-center gap-2 text-sm font-medium text-[var(--color-muted)] hover:text-[var(--color-ink)] transition-colors">
              <PlayIcon className="w-5 h-5" />
              Watch Demo
            </button>
          </motion.div>

          <motion.div
            {...fadeIn(1.3)}
            className="mt-8 flex flex-col sm:flex-row gap-4"
          >
            <div className="card-flat p-5 w-[220px] text-left">
              <ClockIcon className="w-5 h-5 text-[var(--color-primary)]" />
              <p className="text-4xl font-bold tracking-[-1px] leading-none mt-4 text-[var(--color-ink)]">
                Real-Time
              </p>
              <p className="text-xs text-[var(--color-muted)] font-light mt-1.5">
                Instant Threat Detection & Response
              </p>
            </div>
            <div className="card-flat p-5 w-[220px] text-left">
              <GlobeIcon className="w-5 h-5 text-[var(--color-primary)]" />
              <p className="text-4xl font-bold tracking-[-1px] leading-none mt-4 text-[var(--color-ink)]">
                99.9%
              </p>
              <p className="text-xs text-[var(--color-muted)] font-light mt-1.5">
                Accuracy Across All Detection Modules
              </p>
            </div>
          </motion.div>
        </div>

        <motion.div
          {...fadeIn(1.4)}
          className="flex flex-col items-center gap-4 pb-8"
        >
          <div className="rounded-full px-5 py-1.5 bg-[var(--color-surface-strong)] border border-[var(--color-hairline)]">
            <span className="text-xs text-[var(--color-muted)] font-light">
              Trusted by security teams at leading organizations worldwide
            </span>
          </div>
          <div className="flex items-center gap-12 md:gap-16">
            {LOGOS.map((name) => (
              <span
                key={name}
                className="text-lg md:text-xl font-semibold tracking-tight text-[var(--color-muted-soft)]"
              >
                {name}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

const CAPABILITIES_DATA = [
  {
    icon: <ScanIcon className="w-5 h-5" />,
    tags: ["URL Analysis", "Phishing Detection", "Safe Browsing", "ML-Powered"],
    title: "Phishing Scanner",
    body: "Analyze URLs in real-time using machine learning, Google Safe Browsing, and multiple threat intelligence sources to detect phishing attempts.",
  },
  {
    icon: <AlertIcon className="w-5 h-5" />,
    tags: ["Voice Analysis", "Scam Detection", "Keywords", "Real-Time"],
    title: "Scam Call Detection",
    body: "Detect fraudulent phone calls using AI-powered voice analysis and keyword detection. Protect your team from social engineering attacks.",
  },
  {
    icon: <LockIcon className="w-5 h-5" />,
    tags: ["SMS Analysis", "Malware Detection", "URL Extraction", "Automated"],
    title: "SMS Threat Scanner",
    body: "Identify phishing and malicious SMS messages instantly. Extract URLs, analyze content, and block threats before they reach your team.",
  },
];

function Capabilities() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-[var(--color-canvas)]">
      <FadingVideo
        src={CAPABILITIES_VIDEO}
        className="absolute inset-0 w-full h-full object-cover z-0 opacity-20"
      />

      <div className="relative z-10 px-8 md:px-16 lg:px-20 pt-24 pb-10 flex flex-col min-h-screen">
        <div className="mb-auto">
          <p className="text-sm text-[var(--color-muted)] mb-6 tracking-wide font-light">
            // Capabilities
          </p>
          <h2 className="text-6xl md:text-7xl lg:text-[6rem] font-semibold leading-[0.9] tracking-[-3px] text-[var(--color-ink)]">
            Security craft,
            <br />
            end to end
          </h2>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          {CAPABILITIES_DATA.map((cap, i) => {
            const anim = fadeIn(0.15 * i);
            return (
              <motion.div
                key={cap.title}
                initial={anim.initial}
                whileInView={anim.animate}
                viewport={{ once: true }}
                transition={anim.transition}
                className="card p-6 min-h-[360px] flex flex-col"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="h-11 w-11 rounded-[var(--radius-sm)] flex items-center justify-center shrink-0 bg-[var(--color-surface-soft)] text-[var(--color-primary)]">
                    {cap.icon}
                  </div>
                  <div className="flex flex-wrap gap-1.5 justify-end">
                    {cap.tags.map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full px-3 py-1 text-[11px] text-[var(--color-muted)] bg-[var(--color-surface-soft)] whitespace-nowrap"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex-1" />

                <h3 className="text-3xl md:text-4xl font-semibold tracking-[-1px] leading-none mt-6 text-[var(--color-ink)]">
                  {cap.title}
                </h3>
                <p className="mt-2 text-sm text-[var(--color-body)] font-light leading-snug max-w-[32ch]">
                  {cap.body}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

export default function App() {
  return (
    <main>
      <Hero />
      <Capabilities />
    </main>
  );
}
