interface Props {
  transcript: string;
}

export default function TranscriptBox({ transcript }: Props) {
  return (
    <div className="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">

      <h2 className="text-xl font-bold text-white mb-4">
        Transcript
      </h2>

      <textarea
        value={transcript}
        readOnly
        rows={8}
        className="w-full rounded-xl bg-slate-900/60 text-white p-4 border border-white/10"
      />

    </div>
  );
}