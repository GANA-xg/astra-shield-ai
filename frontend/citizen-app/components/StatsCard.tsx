interface Props {
  title: string;
  value: string | number;
  color: string;
}

export default function StatsCard({
  title,
  value,
  color,
}: Props) {
  return (
    <div className={`rounded-2xl p-6 shadow-lg ${color}`}>
      <p className="text-sm font-medium text-white/80">
        {title}
      </p>

      <h2 className="mt-2 text-4xl font-bold text-white">
        {value}
      </h2>
    </div>
  );
}