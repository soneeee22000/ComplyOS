"use client";

import { useState } from "react";
import {
  Loader2,
  Search,
  AlertCircle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronUp,
  FileText,
  Download,
  ClipboardCopy,
} from "lucide-react";
import type { AISystem, GapAnalysisResult } from "@/lib/api";
import { api } from "@/lib/api";

interface GapAnalysisPanelProps {
  system: AISystem;
}

const severityConfig: Record<
  string,
  { icon: typeof AlertCircle; style: string; label: string }
> = {
  critical: {
    icon: AlertCircle,
    style: "text-destructive bg-destructive/10 border-destructive/20",
    label: "Critical",
  },
  major: {
    icon: AlertTriangle,
    style: "text-accent-foreground bg-accent/10 border-accent/20",
    label: "Major",
  },
  minor: {
    icon: Info,
    style: "text-primary bg-primary/10 border-primary/20",
    label: "Minor",
  },
};

export function GapAnalysisPanel({ system }: GapAnalysisPanelProps) {
  const [result, setResult] = useState<GapAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [expandedGap, setExpandedGap] = useState<number | null>(null);
  const [generatingDoc, setGeneratingDoc] = useState(false);
  const [generatedDoc, setGeneratedDoc] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setError("");
    try {
      const data = await api.analyzeSystem(system.id);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGenerateDoc = async () => {
    setGeneratingDoc(true);
    try {
      const doc = await api.generateDocs(system.id, "technical_documentation");
      setGeneratedDoc(doc.content);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Document generation failed",
      );
    } finally {
      setGeneratingDoc(false);
    }
  };

  const handleCopyDoc = () => {
    if (generatedDoc) {
      navigator.clipboard.writeText(generatedDoc);
    }
  };

  if (!system.risk_level || system.risk_level !== "high") {
    return null;
  }

  return (
    <div className="mt-6">
      {!result && !analyzing && (
        <button
          onClick={handleAnalyze}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border-2 border-dashed border-primary/30 text-primary text-sm font-medium hover:bg-primary/5 hover:border-primary/50 transition-colors"
        >
          <Search className="w-4 h-4" />
          Run Compliance Gap Analysis
        </button>
      )}

      {analyzing && (
        <div className="text-center py-8 rounded-xl border border-border bg-card">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-sm text-muted-foreground">
            Analyzing compliance against Articles 9-15...
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            Checking risk management, data governance, documentation, logging,
            transparency, human oversight, accuracy
          </p>
        </div>
      )}

      {error && <p className="text-sm text-destructive mt-2">{error}</p>}

      {result && (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <div className="p-5 border-b border-border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-foreground">Gap Analysis</h3>
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">Score:</span>
                <span
                  className={`text-lg font-bold ${
                    result.overall_score >= 70
                      ? "text-success"
                      : result.overall_score >= 40
                        ? "text-accent"
                        : "text-destructive"
                  }`}
                >
                  {result.overall_score}%
                </span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">{result.summary}</p>
          </div>

          {result.priority_actions.length > 0 && (
            <div className="p-5 border-b border-border bg-destructive/5">
              <h4 className="text-sm font-medium text-foreground mb-2">
                Priority Actions
              </h4>
              <ol className="flex flex-col gap-1.5">
                {result.priority_actions.map((action, index) => (
                  <li
                    key={index}
                    className="text-sm text-foreground flex gap-2"
                  >
                    <span className="text-destructive font-bold shrink-0">
                      {index + 1}.
                    </span>
                    {action}
                  </li>
                ))}
              </ol>
            </div>
          )}

          <div className="divide-y divide-border">
            {result.gaps.map((gap, index) => {
              const config =
                severityConfig[gap.severity] || severityConfig.minor;
              const Icon = config.icon;
              const isExpanded = expandedGap === index;

              return (
                <div key={index} className="p-4">
                  <button
                    onClick={() => setExpandedGap(isExpanded ? null : index)}
                    className="w-full flex items-start gap-3 text-left"
                  >
                    <div
                      className={`w-6 h-6 rounded flex items-center justify-center shrink-0 mt-0.5 border ${config.style}`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-foreground">
                          {gap.requirement}
                        </span>
                        <span className="text-xs text-muted-foreground font-mono">
                          {gap.article}
                        </span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                        {gap.description}
                      </p>
                    </div>
                    <div className="shrink-0 ml-2">
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-muted-foreground" />
                      )}
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="mt-3 ml-9 flex flex-col gap-3">
                      <div>
                        <span className="text-xs font-medium text-muted-foreground uppercase">
                          Gap Description
                        </span>
                        <p className="text-sm text-foreground mt-1">
                          {gap.description}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-muted-foreground uppercase">
                          Remediation
                        </span>
                        <p className="text-sm text-foreground mt-1">
                          {gap.remediation}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div>
                          <span className="text-xs font-medium text-muted-foreground uppercase">
                            Effort
                          </span>
                          <p className="text-sm text-foreground mt-0.5">
                            {gap.estimated_effort}
                          </p>
                        </div>
                        <div>
                          <span className="text-xs font-medium text-muted-foreground uppercase">
                            Status
                          </span>
                          <p className="text-sm text-foreground mt-0.5 capitalize">
                            {gap.status.replace(/_/g, " ")}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="p-5 border-t border-border bg-secondary/30">
            {!generatedDoc ? (
              <button
                onClick={handleGenerateDoc}
                disabled={generatingDoc}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {generatingDoc ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Generating Documentation...
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    Generate Compliance Documentation
                  </>
                )}
              </button>
            ) : (
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-medium text-foreground flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Technical Documentation
                  </h4>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyDoc}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-xs font-medium hover:bg-secondary/80 transition-colors"
                    >
                      <ClipboardCopy className="w-3 h-3" />
                      Copy
                    </button>
                    <button
                      onClick={() => {
                        const blob = new Blob([generatedDoc], {
                          type: "text/markdown",
                        });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = `${system.name.replace(/\s+/g, "-")}-compliance-docs.md`;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors"
                    >
                      <Download className="w-3 h-3" />
                      Download
                    </button>
                  </div>
                </div>
                <div className="max-h-96 overflow-y-auto rounded-lg border border-border bg-background p-4">
                  <pre className="text-xs text-foreground whitespace-pre-wrap font-mono leading-relaxed">
                    {generatedDoc}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
