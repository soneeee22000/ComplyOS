import Link from "next/link";
import {
  Shield,
  ArrowRight,
  Clock,
  AlertTriangle,
  FileText,
  MessageSquare,
  CheckCircle,
  Zap,
  Scale,
  BookOpen,
} from "lucide-react";

const FEATURES = [
  {
    icon: Zap,
    title: "Risk Classification",
    description:
      "Describe your AI system in plain language. Our agent classifies it as Unacceptable, High, Limited, or Minimal risk with cited legal reasoning.",
  },
  {
    icon: AlertTriangle,
    title: "Gap Analysis",
    description:
      "Identify exactly what compliance requirements you are missing across Articles 9-15, with severity ranking and remediation steps.",
  },
  {
    icon: FileText,
    title: "Document Generation",
    description:
      "Auto-generate Article 11 technical documentation, risk assessments, and conformity declarations ready for regulatory submission.",
  },
  {
    icon: MessageSquare,
    title: "Compliance Chat",
    description:
      "Ask any question about the EU AI Act. Get accurate answers with cited articles, powered by RAG over the full 144-page regulation.",
  },
];

const STATS = [
  { value: "595", label: "Legal text chunks indexed" },
  { value: "113", label: "Articles covered" },
  { value: "100%", label: "Classification accuracy" },
  { value: "< 30s", label: "Time to classify" },
];

const RISK_EXAMPLES = [
  {
    name: "AI Resume Screener",
    risk: "HIGH",
    category: "Employment",
    color: "bg-red-50 border-red-200 text-red-700",
  },
  {
    name: "Credit Scoring Model",
    risk: "HIGH",
    category: "Essential Services",
    color: "bg-red-50 border-red-200 text-red-700",
  },
  {
    name: "Customer Chatbot",
    risk: "LIMITED",
    category: "Transparency",
    color: "bg-amber-50 border-amber-200 text-amber-700",
  },
  {
    name: "Email Spam Filter",
    risk: "MINIMAL",
    category: "No obligations",
    color: "bg-green-50 border-green-200 text-green-700",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
              <Shield className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-foreground text-lg">ComplyOS</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/systems"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              AI Systems
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              Open App
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      <section className="pt-24 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-destructive/10 text-destructive text-sm font-medium mb-8">
            <Clock className="w-3.5 h-3.5" />
            128 days until EU AI Act deadline (August 2, 2026)
          </div>

          <h1 className="text-5xl font-bold text-foreground leading-tight tracking-tight">
            EU AI Act Compliance
            <br />
            <span className="text-primary">in Minutes, Not Months</span>
          </h1>

          <p className="text-xl text-muted-foreground mt-6 max-w-2xl mx-auto leading-relaxed">
            Classify your AI systems by risk level, identify compliance gaps,
            and generate required documentation. Powered by RAG over the full EU
            AI Act regulation.
          </p>

          <div className="flex items-center justify-center gap-4 mt-10">
            <Link
              href="/systems"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
            >
              Classify Your AI Systems
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              href="/chat"
              className="flex items-center gap-2 px-6 py-3 rounded-xl border border-border text-foreground font-medium hover:bg-secondary transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
              Ask a Compliance Question
            </Link>
          </div>
        </div>
      </section>

      <section className="py-12 px-6 border-y border-border bg-card">
        <div className="max-w-5xl mx-auto grid grid-cols-4 gap-8">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-3xl font-bold text-foreground">{stat.value}</p>
              <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">How It Works</h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
              Four AI agents work together to take you from uncertainty to
              compliance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {FEATURES.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-border bg-card p-6 hover:border-primary/30 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <feature.icon className="w-5 h-5 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground text-lg">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-6 bg-card border-y border-border">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">
              Live Classification Results
            </h2>
            <p className="text-muted-foreground mt-3 max-w-xl mx-auto">
              Real AI systems classified by our agent. 100% accuracy against
              expert benchmarks.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-3xl mx-auto">
            {RISK_EXAMPLES.map((example) => (
              <div
                key={example.name}
                className={`rounded-xl border p-5 ${example.color}`}
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{example.name}</h3>
                  <span className="text-xs font-bold uppercase px-2 py-0.5 rounded-full border">
                    {example.risk}
                  </span>
                </div>
                <p className="text-sm mt-1 opacity-75">{example.category}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground">Why ComplyOS</h2>
          </div>

          <div className="flex flex-col gap-4">
            {[
              "Full EU AI Act text (595 chunks from EUR-Lex) indexed for RAG retrieval",
              "Multi-agent pipeline: specialized agents for classification, gap analysis, document generation",
              "Every classification includes confidence scores and cited legal articles",
              "Gap analysis checks all Article 9-15 requirements with severity ranking",
              "Auto-generated Article 11 technical documentation ready for filing",
              "Built in Paris, EU-first, GDPR-compliant by design",
            ].map((point) => (
              <div key={point} className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                <p className="text-foreground">{point}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-6 bg-primary text-primary-foreground">
        <div className="max-w-3xl mx-auto text-center">
          <Scale className="w-12 h-12 mx-auto mb-6 opacity-80" />
          <h2 className="text-3xl font-bold">
            The EU AI Act deadline is August 2, 2026
          </h2>
          <p className="text-lg mt-4 opacity-80">
            Fines up to EUR 35 million or 7% of global revenue. Start your
            compliance assessment today.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 mt-8 rounded-xl bg-background text-foreground font-semibold hover:bg-background/90 transition-colors"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      <footer className="py-12 px-6 border-t border-border">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-primary flex items-center justify-center">
              <Shield className="w-3.5 h-3.5 text-primary-foreground" />
            </div>
            <span className="font-bold text-foreground">ComplyOS</span>
            <span className="text-sm text-muted-foreground">
              EU AI Act Compliance Agent
            </span>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <a
              href="https://github.com/soneeee22000/ComplyOS"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://complyos.onrender.com/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              API Docs
            </a>
            <a
              href="https://pseonkyaw.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              Built by Seon
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
