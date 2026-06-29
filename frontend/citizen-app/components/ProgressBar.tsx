interface ProgressBarProps {
  score: number;
}

export default function ProgressBar({ score }: ProgressBarProps) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm font-medium text-gray-700">
        <span>Risk Score</span>
        <span>{score}/100</span>
      </div>

      <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200">
        <div
          className="h-full rounded-full bg-red-500 transition-all duration-700"
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}