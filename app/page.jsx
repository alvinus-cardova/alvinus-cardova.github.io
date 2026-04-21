import Link from "next/link";
import FloatingOrbs from "../components/FloatingOrbs";
import RevealInView from "../components/RevealInView";

const interests = [
  {
    title: "LLM + Agentic Workflows",
    description:
      "Designing assistants that combine reasoning, tools, and memory to automate real business tasks."
  },
  {
    title: "RAG Architecture",
    description:
      "Building reliable retrieval pipelines for enterprise knowledge search, Q&A, and contextual summarization."
  },
  {
    title: "NLP + Computer Vision",
    description:
      "Applying OCR, object detection, and text intelligence into production-ready pipelines."
  }
];

const specialist = [
  "Build and optimize NLP, LLM, and computer vision models for applied use cases.",
  "Develop robust inference APIs with FastAPI and production-aware deployment workflows.",
  "Improve model quality using evaluation loops, observability, and structured feedback.",
  "Balance model quality, latency, and cost for real-world operational constraints."
];

const projects = [
  {
    title: "Senovtik Seminar",
    description:
      "Open-source Indonesian sentiment analysis initiative focused on social media intelligence.",
    href: "https://sinovik.menpan.go.id/",
    label: "View Project"
  },
  {
    title: "Research Reproduction",
    description:
      "Reimplemented fake-news detection research and documented reproducible technical findings.",
    href: "https://ejurnal.umri.ac.id/index.php/JIK/article/view/6175",
    label: "View Publication"
  },
  {
    title: "ANPR Pipeline",
    description:
      "License plate recognition workflow using YOLOv8 + EasyOCR with Streamlit interaction.",
    href: "/portfolio/",
    label: "View Portfolio"
  }
];

const stack = [
  "Python",
  "SQL",
  "PyTorch",
  "scikit-learn",
  "LangChain",
  "LlamaIndex",
  "FastAPI",
  "Streamlit",
  "Docker",
  "GSAP",
  "Framer Motion",
  "Vector DB"
];

export default function Home() {
  return (
    <main className="relative min-h-screen bg-hero-gradient">
      <FloatingOrbs />

      <div className="noise-overlay pointer-events-none fixed inset-0 z-0" aria-hidden />

      <div className="relative z-10">
        <header className="sticky top-0 z-30 border-b border-white/55 bg-white/65 backdrop-blur-md">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 md:px-8">
            <div className="font-display text-lg font-semibold tracking-tight text-ink">
              Alvinus Cardova
            </div>
            <nav className="hidden items-center gap-5 text-sm font-semibold text-slate-700 md:flex">
              <a href="#about" className="transition hover:text-ocean">
                About
              </a>
              <a href="#interests" className="transition hover:text-ocean">
                Interests
              </a>
              <a href="#projects" className="transition hover:text-ocean">
                Projects
              </a>
              <a href="#contact" className="transition hover:text-ocean">
                Contact
              </a>
            </nav>
          </div>
        </header>

        <div className="mx-auto flex w-full max-w-6xl flex-col gap-5 px-5 pb-14 pt-10 md:px-8 md:pt-16">
          <RevealInView className="grid gap-4 lg:grid-cols-[1.14fr,0.86fr]">
            <section className="glass-panel p-6 md:p-8">
              <span className="pill-badge">AI Engineer Portfolio</span>
              <h1 className="mt-4 font-display text-3xl font-semibold leading-tight text-ink md:text-5xl">
                Building Modern AI Systems From Prototype to Production
              </h1>
              <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-700 md:text-lg">
                I build practical AI products using LLMs, RAG, and machine learning pipelines.
                My focus is shipping reliable systems with strong evaluation, maintainable APIs,
                and measurable business impact.
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <a className="btn" href="/files/CV_Alvinus%20Cardova.pdf">
                  Download CV
                </a>
                <a
                  className="btn btn--inverse"
                  href="https://github.com/alvinus-cardova"
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub
                </a>
                <a className="btn btn--inverse" href="mailto:alvinuscardova16@gmail.com">
                  Collaborate
                </a>
              </div>

              <div className="mt-7 grid gap-3 sm:grid-cols-3">
                <div className="stat-chip">
                  <span>Primary Focus</span>
                  <strong>LLM + RAG</strong>
                </div>
                <div className="stat-chip">
                  <span>Delivery Focus</span>
                  <strong>API + MLOps</strong>
                </div>
                <div className="stat-chip">
                  <span>Specialization</span>
                  <strong>NLP + Vision</strong>
                </div>
              </div>
            </section>

            <section className="glass-panel overflow-hidden p-4 md:p-5">
              <img
                className="h-full w-full rounded-2xl border border-sky-100 object-cover shadow-glow"
                src="/images/tech_image1.png"
                alt="AI engineering illustration"
              />
            </section>
          </RevealInView>

          <RevealInView id="about" className="glass-panel p-6 md:p-8" delay={0.05}>
            <h2 className="section-title">About Me</h2>
            <p className="mt-4 max-w-4xl leading-relaxed text-slate-700">
              I am Alvinus Cardova, an AI Engineer focused on designing systems that are useful
              in production, not only in experimentation. I combine engineering discipline,
              machine learning experimentation, and product thinking to deliver AI that teams can
              trust in daily operations.
            </p>
          </RevealInView>

          <section id="interests" className="glass-panel p-6 md:p-8">
            <h2 className="section-title">Data Science Interests</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {interests.map((item, index) => (
                <RevealInView key={item.title} delay={0.08 * index}>
                  <article className="portfolio-card h-full">
                    <h3 className="font-display text-lg font-semibold text-ink">{item.title}</h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-700">
                      {item.description}
                    </p>
                  </article>
                </RevealInView>
              ))}
            </div>
          </section>

          <RevealInView className="glass-panel p-6 md:p-8" delay={0.08}>
            <h2 className="section-title">Machine Learning Specialist</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {specialist.map((point, index) => (
                <article key={point} className="portfolio-card">
                  <p className="text-sm leading-relaxed text-slate-700">
                    <span className="font-semibold text-ocean">0{index + 1}. </span>
                    {point}
                  </p>
                </article>
              ))}
            </div>
          </RevealInView>

          <section id="projects" className="glass-panel p-6 md:p-8">
            <h2 className="section-title">Selected Projects</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {projects.map((project, index) => (
                <RevealInView key={project.title} delay={0.07 * index}>
                  <article className="portfolio-card h-full">
                    <h3 className="font-display text-lg font-semibold text-ink">
                      {project.title}
                    </h3>
                    <p className="mt-2 text-sm leading-relaxed text-slate-700">
                      {project.description}
                    </p>
                    {project.href.startsWith("/") ? (
                      <Link
                        href={project.href}
                        className="mt-4 inline-block text-sm font-semibold uppercase tracking-wide text-ocean transition hover:text-teal"
                      >
                        {project.label}
                      </Link>
                    ) : (
                      <a
                        className="mt-4 inline-block text-sm font-semibold uppercase tracking-wide text-ocean transition hover:text-teal"
                        href={project.href}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {project.label}
                      </a>
                    )}
                  </article>
                </RevealInView>
              ))}
            </div>
          </section>

          <RevealInView className="glass-panel bg-gradient-to-r from-blue-100/70 to-teal-100/70 p-6 md:p-8">
            <h2 className="section-title">Tech Stack</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {stack.map((item) => (
                <span key={item} className="tag-chip">
                  {item}
                </span>
              ))}
            </div>
          </RevealInView>

          <RevealInView id="contact" className="glass-panel text-center p-6 md:p-10" delay={0.12}>
            <h2 className="section-title">Open To AI Engineering Collaborations</h2>
            <p className="mx-auto mt-3 max-w-2xl text-slate-700">
              If you are building AI-driven products and need support from architecture to
              deployment, let&apos;s build something impactful together.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <a className="btn" href="mailto:alvinuscardova16@gmail.com">
                Start a Conversation
              </a>
              <a
                className="btn btn--inverse"
                href="https://www.linkedin.com/in/alvinuscardova"
                target="_blank"
                rel="noreferrer"
              >
                LinkedIn
              </a>
              <a
                className="btn btn--inverse"
                href="https://www.youtube.com/@alvinuscardova9407"
                target="_blank"
                rel="noreferrer"
              >
                YouTube
              </a>
            </div>
          </RevealInView>
        </div>
      </div>
    </main>
  );
}
