"use client";

import { motion } from "framer-motion";

const navItems = ["Resume", "Showcase", "Blog", "Resources", "AI_Chat", "Games"];
const skills = [
  "Artificial Intelligence",
  "Data Analysis",
  "UI/UX",
  "Problem Solving",
  "Management",
  "Teamwork",
  "Project Management"
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f4f4f5] text-[#0f172a]">
      <div className="mx-auto w-full max-w-[1140px] px-4 pb-20 pt-4 sm:px-6">
        <header className="flex items-center justify-between">
          <a href="/" className="font-display text-[2.1rem] font-bold leading-none tracking-tight text-black">
            Why
          </a>

          <div className="flex items-center gap-6">
            <nav className="hidden items-center gap-7 lg:flex">
              {navItems.map((item) => (
                <a
                  key={item}
                  href="#"
                  className={`text-[1.05rem] font-semibold tracking-tight transition ${
                    item === "Resume" ? "text-[#1491e5]" : "text-[#111827] hover:text-[#1491e5]"
                  }`}
                >
                  {item}
                </a>
              ))}
            </nav>

            <button
              type="button"
              aria-label="Search"
              className="inline-flex h-10 w-10 items-center justify-center rounded-full text-[#111827] transition hover:bg-white"
            >
              <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="7" />
                <path d="m20 20-3.2-3.2" />
              </svg>
            </button>

            <button
              type="button"
              aria-label="Theme"
              className="inline-flex h-12 w-12 items-center justify-center rounded-lg border border-[#d4d4d8] bg-[#f7f7f8] text-[#111827]"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2.5M12 19.5V22M4.93 4.93l1.77 1.77M17.3 17.3l1.77 1.77M2 12h2.5M19.5 12H22M4.93 19.07l1.77-1.77M17.3 6.7l1.77-1.77" />
              </svg>
            </button>
          </div>
        </header>

        <motion.section
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          className="pt-12"
        >
          <h1 className="font-display text-[3.6rem] font-bold leading-[1.02] tracking-tight text-[#0f172a] md:text-[4.3rem]">
            My Resume
          </h1>
        </motion.section>

        <hr className="mt-8 border-[#d8d8dd]" />

        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
          className="mt-10 grid gap-12 lg:grid-cols-[320px_minmax(0,1fr)]"
        >
          <aside className="text-center">
            <div className="mx-auto w-fit">
              <img
                src="/images/fotoku2.png"
                alt="avatar"
                className="h-[220px] w-[220px] rounded-full object-cover"
              />
              <p className="mt-2 text-sm text-[#8f8f96]">avatar</p>
            </div>

            <h2 className="mt-5 font-display text-[2.35rem] font-bold leading-tight tracking-tight text-[#0f172a]">
              Alvinus Cardova
            </h2>
            <p className="mt-3 text-[1.25rem] leading-snug text-[#4b5563]">
              AI Engineer and Data Science Practitioner
            </p>
            <p className="mt-1 text-[1.25rem] leading-snug text-[#4b5563]">Yogyakarta, Indonesia</p>

            <button
              type="button"
              className="mt-6 inline-flex items-center justify-center rounded-full border border-[#d4d4d8] px-7 py-3 text-[1.02rem] font-semibold text-[#111827] transition hover:bg-white"
            >
              Chat with My AI Assistant
            </button>
          </aside>

          <article className="space-y-8">
            <p className="text-[1.06rem] leading-[1.7] text-[#273244]">
              Applied Data Science student at Yogyakarta University of Technology, currently focused on AI engineering
              and production-ready machine learning systems.
            </p>

            <p className="text-[1.06rem] leading-[1.7] text-[#273244]">
              AI Engineer with 3 years of freelance experience, actively working on projects from enterprise analytics
              to intelligent automation solutions. Active in creating technical content, contributing to open source
              projects, and publishing practical notes on AI implementation.
            </p>

            <p className="text-[1.06rem] leading-[1.7] text-[#273244]">
              I am deeply passionate about building useful AI products, especially in LLM systems, data engineering,
              computer vision, and machine learning operations.
            </p>

            <section>
              <h3 className="font-display text-[2rem] font-bold tracking-tight text-[#0f172a]">My Skill</h3>
              <div className="mt-4 flex flex-wrap gap-2.5">
                {skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full border border-[#d1d5db] px-4 py-1.5 text-[0.93rem] font-medium text-[#334155]"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </section>

            <section>
              <h3 className="font-display text-[2rem] font-bold tracking-tight text-[#0f172a]">Education</h3>
              <p className="mt-4 text-[1.08rem] leading-[1.7] text-[#273244]">Yogyakarta University of Technology</p>
              <p className="text-[1.08rem] leading-[1.7] text-[#273244]">Applied Data Science</p>
            </section>

            <section className="space-y-5 pt-2">
              <p className="font-display text-[2.2rem] font-bold tracking-tight text-[#0f172a]">15+ Project</p>
              <p className="font-display text-[2.2rem] font-bold tracking-tight text-[#0f172a]">50+ Certificate</p>
            </section>
          </article>
        </motion.section>
      </div>
    </main>
  );
}
