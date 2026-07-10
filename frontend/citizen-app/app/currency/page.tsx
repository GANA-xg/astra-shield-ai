import CurrencyScanner from "@/components/CurrencyScanner";

export default function CurrencyPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8">
      <div className="mx-auto max-w-3xl">
        <h1 className="mb-2 text-4xl font-bold text-white">
          Currency Counterfeit Detection
        </h1>

        <p className="mb-8 text-slate-300">
          Upload an image of a currency note to verify whether it is genuine or counterfeit.
        </p>

        <CurrencyScanner />
      </div>
    </main>
  );
}