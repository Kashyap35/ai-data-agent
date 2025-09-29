import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#0088FE"];

export default function ChartRenderer({ columns, rows }) {
  if (!columns || !rows || rows.length === 0) return null;

  // detect columns
  const lowerCols = columns.map((c) => String(c).toLowerCase());

  const timeIdx = lowerCols.findIndex((c) =>
    ["date", "day", "month", "year"].some((kw) => c.includes(kw))
  );
  const stringIdx = lowerCols.findIndex((c) =>
    rows.some((r) => typeof r[columns.indexOf(c)] === "string")
  );
  const numericIdx = lowerCols.findIndex((c) =>
    rows.some((r) => typeof r[columns.indexOf(c)] === "number")
  );

  if (stringIdx === -1 || numericIdx === -1) return null;

  // build data
  const data = rows.map((row, i) => ({
    label: String(row[stringIdx] ?? i),
    value: Number(row[numericIdx]) || 0,
  }));

  // 1) Time series → Line chart
  if (timeIdx !== -1) {
    return (
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // 2) Few categories → Pie chart
  if (data.length <= 6) {
    return (
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="label"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // 3) Default → Bar chart
  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="value" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
