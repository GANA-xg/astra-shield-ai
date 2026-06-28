interface RiskBadgeProps {
  level: string;
}

export default function RiskBadge({ level }: RiskBadgeProps) {
  const styles: Record<string, string> = {
    CRITICAL: "bg-red-100 text-red-700",
    HIGH: "bg-orange-100 text-orange-700",
    MEDIUM: "bg-yellow-100 text-yellow-700",
    LOW: "bg-green-100 text-green-700",
  };

  return (
    <span
      className={`rounded-full px-4 py-2 text-sm font-bold ${
        styles[level] ?? styles.LOW
      }`}
    >
      {level}
    </span>
  );
}