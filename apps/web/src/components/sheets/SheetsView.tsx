'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Table2,
  Plus,
  MoreVertical,
  Edit3,
  Trash2,
  Download,
  Search,
  Filter,
} from 'lucide-react'
import { Sheet, SheetRow } from '@/types'

const mockSheet: Sheet = {
  id: '1',
  name: 'Leads Database',
  type: 'leads',
  columns: [
    { id: 'name', name: 'Name', type: 'text' },
    { id: 'email', name: 'Email', type: 'email' },
    { id: 'company', name: 'Company', type: 'text' },
    { id: 'status', name: 'Status', type: 'select', options: ['New', 'Contacted', 'Qualified', 'Won', 'Lost'] },
    { id: 'score', name: 'Score', type: 'number' },
  ],
  rows: [
    {
      id: '1',
      data: {
        name: 'Maya Singh',
        email: 'maya@acme.com',
        company: 'Acme Corp',
        status: 'Qualified',
        score: 85,
      },
      createdAt: new Date(2025, 10, 15),
      updatedAt: new Date(2025, 10, 15),
    },
    {
      id: '2',
      data: {
        name: 'John Doe',
        email: 'john@techco.com',
        company: 'TechCo',
        status: 'Contacted',
        score: 72,
      },
      createdAt: new Date(2025, 10, 14),
      updatedAt: new Date(2025, 10, 14),
    },
    {
      id: '3',
      data: {
        name: 'Sarah Johnson',
        email: 'sarah@startup.io',
        company: 'Startup Inc',
        status: 'New',
        score: 68,
      },
      createdAt: new Date(2025, 10, 13),
      updatedAt: new Date(2025, 10, 13),
    },
  ],
  createdAt: new Date(2025, 10, 1),
  updatedAt: new Date(2025, 10, 15),
}

export function SheetsView() {
  const [sheets] = useState<Sheet[]>([mockSheet])
  const [activeSheet, setActiveSheet] = useState<Sheet>(mockSheet)
  const [searchQuery, setSearchQuery] = useState('')

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      New: 'bg-blue-500/20 text-blue-500',
      Contacted: 'bg-yellow-500/20 text-yellow-500',
      Qualified: 'bg-green-500/20 text-green-500',
      Won: 'bg-purple-500/20 text-purple-500',
      Lost: 'bg-red-500/20 text-red-500',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-500'
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-7xl mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Table2 className="w-6 h-6 text-brand-primary" />
              Sheets
            </h1>
            <button className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New Sheet
            </button>
          </div>

          {/* Sheet Tabs */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {sheets.map((sheet) => (
              <button
                key={sheet.id}
                onClick={() => setActiveSheet(sheet)}
                className={`px-4 py-2 rounded-ai text-sm font-medium whitespace-nowrap transition-all ${
                  activeSheet.id === sheet.id
                    ? 'bg-brand-primary text-white'
                    : 'bg-dark-hover text-dark-text-secondary hover:text-dark-text-primary'
                }`}
              >
                {sheet.name}
              </button>
            ))}
          </div>

          {/* Search and Actions */}
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-text-tertiary" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search rows..."
                className="input-primary pl-11"
              />
            </div>
            <div className="flex gap-2">
              <button className="btn-secondary flex items-center gap-2">
                <Filter className="w-4 h-4" />
                Filter
              </button>
              <button className="btn-secondary flex items-center gap-2">
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Table Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-border bg-dark-hover">
                    <th className="px-4 py-3 text-left text-sm font-semibold text-dark-text-primary">
                      <input
                        type="checkbox"
                        className="w-4 h-4 rounded border-dark-border"
                      />
                    </th>
                    {activeSheet.columns.map((column) => (
                      <th
                        key={column.id}
                        className="px-4 py-3 text-left text-sm font-semibold text-dark-text-primary whitespace-nowrap"
                      >
                        {column.name}
                      </th>
                    ))}
                    <th className="px-4 py-3 text-right text-sm font-semibold text-dark-text-primary">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {activeSheet.rows.map((row, index) => (
                    <motion.tr
                      key={row.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b border-dark-border hover:bg-dark-hover transition-colors"
                    >
                      <td className="px-4 py-3">
                        <input
                          type="checkbox"
                          className="w-4 h-4 rounded border-dark-border"
                        />
                      </td>
                      {activeSheet.columns.map((column) => (
                        <td
                          key={column.id}
                          className="px-4 py-3 text-sm text-dark-text-primary whitespace-nowrap"
                        >
                          {column.type === 'select' ? (
                            <span
                              className={`px-2 py-1 rounded-ai-sm text-xs font-medium ${getStatusColor(
                                row.data[column.id]
                              )}`}
                            >
                              {row.data[column.id]}
                            </span>
                          ) : column.type === 'email' ? (
                            <a
                              href={`mailto:${row.data[column.id]}`}
                              className="text-brand-primary hover:underline"
                            >
                              {row.data[column.id]}
                            </a>
                          ) : (
                            row.data[column.id]
                          )}
                        </td>
                      ))}
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button className="btn-icon p-1.5">
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button className="btn-icon p-1.5 hover:text-red-500">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Row Button */}
          <button className="mt-4 w-full py-3 border-2 border-dashed border-dark-border rounded-ai hover:border-brand-primary hover:bg-dark-surface transition-all text-dark-text-tertiary hover:text-brand-primary flex items-center justify-center gap-2">
            <Plus className="w-4 h-4" />
            Add Row
          </button>
        </div>
      </div>
    </div>
  )
}
