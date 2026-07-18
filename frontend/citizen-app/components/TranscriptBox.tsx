interface Props {
  transcript: string;
}

export default function TranscriptBox({ transcript }: Props) {
  return (
    <div className="card-flat p-6">
      <h3 className="text-lg font-semibold text-[var(--ink)] mb-4">Transcript</h3>
      <textarea
        value={transcript}
        readOnly
        rows={8}
        className="input-field h-auto min-h-[120px] resize-none bg-[var(--surface-soft)]"
      />
    </div>
  );
}
