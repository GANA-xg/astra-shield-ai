import React from "react";

const ResultCard = ({ result }) => {
  return (
    <div>
      {/* Other cards */}
      <div className="rounded-xl border border-orange-200 bg-orange-50 p-5">
        <h3 className="text-sm font-semibold text-slate-800">Blacklist Matches</h3>
        <div className="mt-4 space-y-2">
          {Object.entries(result.blacklists).map(([key, value]) => (
            <div
              key={key}
              className="flex items-center justify-between rounded-md bg-white px-3 py-2"
            >
              <span className="font-medium text-slate-900">{key}</span>
              <span className={value ? "font-bold text-red-700" : "font-bold text-green-700"}>
                {value ? "Matched" : "Not Matched"}
              </span>
            </div>
          ))}
        </div>
      </div>
      {/* Other cards */}
    </div>
  );
};

export default ResultCard;
