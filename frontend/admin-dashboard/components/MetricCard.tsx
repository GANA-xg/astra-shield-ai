interface Props {
  title: string;
  value: number | string;
  icon: string;
  color: string;
}

export default function MetricCard({ title, value, icon, color }: Props) {
  return (
    <div className={`card p-6 ${color}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-white/70">{title}</p>
          <h2 className="mt-2 text-3xl font-bold text-white">{value}</h2>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
}
