import { getMoneyMules } from "@/lib/api";

export default async function FraudNetworkPage() {
  const moneyMules = await getMoneyMules();

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">
        Fraud Network Intelligence
      </h1>

      <p className="text-gray-500 mt-2">
        Agent 3 Investigation Dashboard
      </p>

      <div className="mt-10">
        <h2 className="text-xl font-semibold mb-4">
          Money Mule Detection
        </h2>

        <table className="w-full border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border p-3">
                Account Number
              </th>

              <th className="border p-3">
                Sender Count
              </th>
            </tr>
          </thead>

          <tbody>
            {moneyMules.map((mule: any) => (
              <tr key={mule.account_number}>
                <td className="border p-3">
                  {mule.account_number}
                </td>

                <td className="border p-3">
                  {mule.sender_count}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}