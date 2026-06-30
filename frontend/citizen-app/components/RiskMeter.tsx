interface Props {
  score: number;
}

export default function RiskMeter({ score }: Props) {
  const color =
    score >= 80
      ? "bg-red-500"
      : score >= 50
      ? "bg-yellow-500"
      : "bg-green-500";

  return (
    <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">

      <h2 className="text-xl font-bold text-white mb-4">
        Risk Score
      </h2>

      <div className="w-full h-8 rounded-full bg-gray-700 overflow-hidden">

        <div
          className={`${color} h-8 flex items-center justify-center font-bold text-white transition-all duration-700`}
          style={{ width: `${score}%` }}
        >
          {score}%
        </div>

      </div>

    </div>
  );
}