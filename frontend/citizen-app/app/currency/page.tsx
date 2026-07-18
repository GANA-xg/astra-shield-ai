import AgentPage from "@/components/AgentPage";
import CurrencyScanner from "@/components/CurrencyScanner";

export default function CurrencyPage() {
  return (
    <AgentPage
      title="Currency Detection"
      description="Upload an image of a currency note to verify whether it is genuine or counterfeit using AI-powered image analysis."
    >
      <div className="card-flat p-6">
        <CurrencyScanner />
      </div>
    </AgentPage>
  );
}
