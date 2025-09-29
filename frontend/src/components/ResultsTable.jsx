import React from 'react'

export default function ResultsTable({columns, rows}){
  if(!columns || columns.length===0) return <div>No tabular result.</div>
  return (
    <table className="min-w-full border">
      <thead>
        <tr>
          {columns.map((c,i)=>(<th key={i} className="border px-2">{c}</th>))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r,ri)=>(
          <tr key={ri}>
            {r.map((cell,ci)=>(<td key={ci} className="border px-2">{String(cell)}</td>))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
