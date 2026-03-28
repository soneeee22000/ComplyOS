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
import type { AISystem, EnhancedGapAnalysisResult } from "@/lib/api";
import { api } from "@/lib/api";
import { RequirementTree } from "@/components/requirement-tree";

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
  const [result, setResult] = useState<EnhancedGapAnalysisResult | null>(null);
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
        <div>
          {result.requirement_statuses &&
          result.requirement_statuses.length > 0 ? (
            <RequirementTree
              requirementStatuses={result.requirement_statuses}
              overallScore={result.overall_score}
            />
          ) : (
            <div className="rounded-xl border border-border bg-card p-5">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-foreground">Gap Analysis</h3>
                <span className="text-lg font-bold text-destructive">
                  {result.overall_score}%
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{result.summary}</p>
            </div>
          )}

          <div className="mt-4 p-5 rounded-xl border border-border bg-secondary/30">
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
