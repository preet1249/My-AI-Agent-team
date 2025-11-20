'use client'

import { useState, useEffect } from 'react'
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
  RefreshCw,
} from 'lucide-react'
import { Sheet, SheetRow } from '@/types'
import { API_URL } from '@/lib/constants'

// Default sheet structure for leads
const leadsSheetColumns = [
  { id: 'email', name: 'Email', type: 'email' as const },
  { id: 'name', name: 'Name', type: 'text' as const },
  { id: 'company', name: 'Company', type: 'text' as const },
  { id: 'niche', name: 'Niche', type: 'text' as const },
  { id: 'oneliner', name: 'One-liner', type: 'text' as const },
  { id: 'score', name: 'Score', type: 'number' as const },
  { id: 'status', name: 'Status', type: 'select' as const, options: ['new', 'contacted', 'qualified', 'won', 'lost'] },
]

export function SheetsView() {
  const [sheets, setSheets] = useState<Sheet[]>([])
  const [activeSheet, setActiveSheet] = useState<Sheet | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  // Fetch leads from API
  useEffect(() => {
    const fetchLeads = async () => {
      try {
        const response = await fetch(`${API_URL}/api/leads/user-123?limit=100`)
        if (response.ok) {
          const data = await response.json()
          if (data.success && data.data) {
            // Map leads to sheet rows
            const rows: SheetRow[] = data.data.map((lead: any) => ({
              id: lead.id,
              data: {
                email: lead.email || '',
                name: lead.name || '',
                company: lead.company || '',
                niche: lead.metadata?.company_keywords?.join(', ') || '',
                oneliner: lead.metadata?.company_description?.slice(0, 100) || '',
                score: lead.score || 0,
                status: lead.status || 'new',
              }
            }))

            const leadsSheet: Sheet = {
              id: 'leads',
              name: 'Leads Database',
              type: 'leads',
              columns: leadsSheetColumns,
              rows,
              createdAt: new Date(),
              updatedAt: new Date(),
            }

            setSheets([leadsSheet])
            setActiveSheet(leadsSheet)
          }
        }
      } catch (error) {
        console.log('Could not fetch leads')
        // Set empty sheet
        const emptySheet: Sheet = {
          id: 'leads',
          name: 'Leads Database',
          type: 'leads',
          columns: leadsSheetColumns,
          rows: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        }
        setSheets([emptySheet])
        setActiveSheet(emptySheet)
      } finally {
        setIsLoading(false)
      }
    }
    fetchLeads()
  }, [])

  const refreshLeads = async () => {
    setIsLoading(true)
    try {
      const response = await fetch(`${API_URL}/api/leads/user-123?limit=100`)
      if (response.ok) {
        const data = await response.json()
        if (data.success && data.data) {
          const rows: SheetRow[] = data.data.map((lead: any) => ({
            id: lead.id,
            data: {
              email: lead.email || '',
              name: lead.name || '',
              company: lead.company || '',
              niche: lead.metadata?.company_keywords?.join(', ') || '',
              oneliner: lead.metadata?.company_description?.slice(0, 100) || '',
              score: lead.score || 0,
              status: lead.status || 'new',
            }
          }))

          if (activeSheet) {
            const updatedSheet = { ...activeSheet, rows }
            setActiveSheet(updatedSheet)
            setSheets([updatedSheet])
          }
        }
      }
    } catch (error) {
      console.log('Could not refresh leads')
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      new: 'bg-blue-500/20 text-blue-500',
      contacted: 'bg-yellow-500/20 text-yellow-500',
      qualified: 'bg-green-500/20 text-green-500',
      won: 'bg-purple-500/20 text-purple-500',
      lost: 'bg-red-500/20 text-red-500',
      needs_enrichment: 'bg-orange-500/20 text-orange-500',
    }
    return colors[status?.toLowerCase()] || 'bg-gray-500/20 text-gray-500'
  }

  // Filter rows by search query
  const filteredRows = activeSheet?.rows.filter(row => {
    if (!searchQuery) return true
    const searchLower = searchQuery.toLowerCase()
    return Object.values(row.data).some(value =>
      String(value).toLowerCase().includes(searchLower)
    )
  }) || []

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-dark-text-tertiary">Loading leads...</p>
        </div>
      </div>
    )
  }

  if (!activeSheet) {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-dark-text-tertiary">No sheets available</p>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      {/* Header */}
      <div className="border-b border-dark-border bg-dark-surface p-6">
        <div className="max-w-7xl mx-auto space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
              <Table2 className="w-6 h-6 text-white" />
              Sheets
            </h1>
            <div className="flex gap-2">
              <button
                onClick={refreshLeads}
                className="btn-secondary flex items-center gap-2"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 text-white ${isLoading ? 'animate-spin' : ''}`} />
                <span className="text-white">Refresh</span>
              </button>
              <button className="btn-primary flex items-center gap-2">
                <Plus className="w-4 h-4 text-dark-bg" />
                <span className="text-dark-bg">New Sheet</span>
              </button>
            </div>
          </div>

          {/* Sheet Tabs */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {sheets.map((sheet) => (
              <button
                key={sheet.id}
                onClick={() => setActiveSheet(sheet)}
                className={`px-4 py-2 rounded-ai text-sm font-medium whitespace-nowrap transition-all ${
                  activeSheet.id === sheet.id
                    ? 'bg-white text-dark-bg'
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
                <Filter className="w-4 h-4 text-white" />
                <span className="text-white">Filter</span>
              </button>
              <button className="btn-secondary flex items-center gap-2">
                <Download className="w-4 h-4 text-white" />
                <span className="text-white">Export</span>
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
                  {filteredRows.length === 0 ? (
                    <tr>
                      <td colSpan={activeSheet.columns.length + 2} className="px-4 py-12 text-center">
                        <Table2 className="w-12 h-12 mx-auto mb-3 text-dark-text-tertiary opacity-50" />
                        <p className="text-dark-text-secondary mb-1">No leads yet</p>
                        <p className="text-sm text-dark-text-tertiary">
                          Ask Jake to find leads: "Find 10 leads in Austin tech companies"
                        </p>
                      </td>
                    </tr>
                  ) : (
                    filteredRows.map((row, index) => (
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
                            className="px-4 py-3 text-sm text-dark-text-primary whitespace-nowrap max-w-xs truncate"
                          >
                            {column.type === 'select' ? (
                              <span
                                className={`px-2 py-1 rounded-ai-sm text-xs font-medium capitalize ${getStatusColor(
                                  row.data[column.id]
                                )}`}
                              >
                                {row.data[column.id]}
                              </span>
                            ) : column.type === 'email' ? (
                              row.data[column.id] ? (
                                <a
                                  href={`mailto:${row.data[column.id]}`}
                                  className="text-blue-400 hover:underline"
                                >
                                  {row.data[column.id]}
                                </a>
                              ) : (
                                <span className="text-dark-text-tertiary">-</span>
                              )
                            ) : column.type === 'number' ? (
                              <span className={`font-medium ${Number(row.data[column.id]) >= 70 ? 'text-green-400' : Number(row.data[column.id]) >= 50 ? 'text-yellow-400' : 'text-dark-text-secondary'}`}>
                                {row.data[column.id]}
                              </span>
                            ) : (
                              row.data[column.id] || <span className="text-dark-text-tertiary">-</span>
                            )}
                          </td>
                        ))}
                        <td className="px-4 py-3 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button className="btn-icon p-1.5">
                              <Edit3 className="w-4 h-4 text-white" />
                            </button>
                            <button className="btn-icon p-1.5 hover:text-red-500">
                              <Trash2 className="w-4 h-4 text-white" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Add Row Button */}
          <button className="mt-4 w-full py-3 border-2 border-dashed border-dark-border rounded-ai hover:border-white hover:bg-dark-surface transition-all text-dark-text-tertiary hover:text-white flex items-center justify-center gap-2">
            <Plus className="w-4 h-4" />
            Add Row
          </button>
        </div>
      </div>
    </div>
  )
}
