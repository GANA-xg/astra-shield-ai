interface Props {
  title: string;
  value: number | string;
  icon: string;
  color: string;
}

export default function MetricCard({
  title,
  value,
  icon,
  color,
}: Props) {
  return (
    <div
      className={`rounded-3xl border border-white/10 bg-white/10 p-6 backdrop-blur-xl shadow-xl transition hover:-translate-y-1 ${color}`}
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-white/70 text-sm">
            {title}
          </p>

          <h2 className="mt-3 text-5xl font-extrabold text-white">
            {value}
          </h2>

        </div>

        <div className="text-5xl">
          {icon}
        </div>

      </div>
    </div>
  );
}