import React, { useState } from "react";
import axios from "axios";
import ResultsTable from "./ResultsTable";
import ChartRenderer from "./ChartRenderer";

export default function QueryBox() {
  const [q, setQ] = useState("");
  const [res, setRes] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    setRes(null);
    try {
      const r = await axios.post(`${import.meta.env.VITE_API_URL}/ask`, { question: q });
      setRes(r.data);
    } catch (err) {
      // show more detail
      const details =
        err?.response?.data ||
        (err.toJSON ? err.toJSON() : { message: err.message });
      setRes({ error: "Network or server error", details });
      console.error("AXIOS ERROR", err);
    } finally {
      setLoading(false);
    }
  };

  // convert response to chart-friendly data when possible
  const chartData = React.useMemo(() => {
    if (!res || !res.columns || !res.rows) return null;
    const cols = res.columns.map((c) => String(c).toLowerCase());
    // common pattern: prod + total_qty / revenue
    const prodIdx = cols.indexOf("prod");
    const qtyIdx = cols.indexOf("total_qty");
    const revenueIdx = cols.indexOf("revenue");

    // fallback: find first string column and first numeric column
    let stringIdx = prodIdx;
    if (stringIdx === -1) {
      stringIdx = cols.findIndex((c, i) =>
        res.rows.some((r) => typeof r[i] === "string")
      );
    }
    let numericIdx = qtyIdx !== -1 ? qtyIdx : revenueIdx;
    if (numericIdx === -1) {
      numericIdx = cols.findIndex((c, i) =>
        res.rows.some((r) => typeof r[i] === "number")
      );
    }

    if (stringIdx === -1 || numericIdx === -1) return null;

    const data = res.rows.map((row) => {
      const obj = {};
      obj["label"] = String(row[stringIdx]);
      obj["value"] = Number(row[numericIdx]) || 0;
      return obj;
    });
    return data;
  }, [res]);

  return (
    <div>
      <textarea
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Ask any business question..."
        className="w-full h-24 p-2 border"
      />
      <div className="flex gap-2 mt-2">
        <button
          onClick={submit}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Ask
        </button>
        <button
          onClick={() => {
            setQ("show top selling products");
          }}
          className="px-4 py-2 bg-gray-200 rounded"
        >
          Example: top selling products
        </button>
      </div>

      {loading && <div className="mt-4">Loading…</div>}

      {res && (
        <div className="mt-4">
          {res.error ? (
            <div className="text-red-600">
              <div>{res.error}</div>
              <pre className="mt-2 p-2 bg-gray-100 text-sm">
                {JSON.stringify(res.details || res, null, 2)}
              </pre>
            </div>
          ) : (
            <>
              <div className="mb-2 font-semibold">Answer</div>
              <div className="mb-4">{res.answer}</div>

              {/* Chart (if available) */}
              {chartData && chartData.length > 0 && (
                <div style={{ width: "100%", height: 300 }} className="mb-4">
                  
                  <ChartRenderer columns={res.columns} rows={res.rows} />

                </div>
              )}

              <ResultsTable columns={res.columns} rows={res.rows} />
              <pre className="mt-2 text-sm bg-gray-100 p-2 break-words">
                {res.sql}
              </pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}
