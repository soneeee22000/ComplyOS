interface RiskBadgeProps {
  level: string | null;
  size?: "sm" | "md";
}

const riskStyles: Record<string, string> = {
  unacceptable: "bg-destructive/10 text-destructive border-destructive/20",
  high: "bg-destructive/10 text-destructive border-destructive/20",
  limited: "bg-accent/10 text-accent-foreground border-accent/20",
  minimal: "bg-success/10 text-success border-success/20",
};

const sizeStyles = {
  sm: "text-xs px-2 py-0.5",
  md: "text-sm px-3 py-1",
};

export function RiskBadge({ level, size = "sm" }: RiskBadgeProps) {
  if (!level) {
    return (
      <span
        className={`inline-flex items-center rounded-full border bg-secondary text-muted-foreground ${sizeStyles[size]}`}
      >
        Not classified
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-full border font-medium uppercase ${riskStyles[level] || riskStyles.minimal} ${sizeStyles[size]}`}
    >
      {level}
    </span>
  );
}
