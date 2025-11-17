'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  ChevronLeft,
  ChevronRight,
  Calendar as CalendarIcon,
  Plus,
  Phone,
  CheckCircle2,
  Clock,
} from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, isToday } from 'date-fns'
import { CalendarEvent } from '@/types'

const mockEvents: CalendarEvent[] = [
  {
    id: '1',
    title: 'Client Call - Acme Corp',
    description: 'Discuss product demo',
    startTime: new Date(2025, 10, 20, 10, 0),
    endTime: new Date(2025, 10, 20, 11, 0),
    type: 'call',
    status: 'pending',
  },
  {
    id: '2',
    title: 'Follow up on leads',
    startTime: new Date(2025, 10, 18, 14, 0),
    endTime: new Date(2025, 10, 18, 15, 0),
    type: 'task',
    status: 'completed',
  },
]

export function CalendarView() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [events] = useState<CalendarEvent[]>(mockEvents)

  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd })

  const previousMonth = () => setCurrentDate(subMonths(currentDate, 1))
  const nextMonth = () => setCurrentDate(addMonths(currentDate, 1))

  const getEventsForDay = (day: Date) => {
    return events.filter((event) => isSameDay(event.startTime, day))
  }

  const selectedDayEvents = getEventsForDay(selectedDate)

  const getEventTypeIcon = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'call':
        return <Phone className="w-3 h-3" />
      case 'task':
        return <CheckCircle2 className="w-3 h-3" />
      default:
        return <Clock className="w-3 h-3" />
    }
  }

  const getEventTypeColor = (type: CalendarEvent['type']) => {
    switch (type) {
      case 'call':
        return 'bg-white'
      case 'task':
        return 'bg-white/70'
      case 'meeting':
        return 'bg-white/50'
      default:
        return 'bg-white/30'
    }
  }

  return (
    <div className="h-full flex flex-col lg:flex-row overflow-hidden">
      {/* Calendar Grid */}
      <div className="flex-1 p-6 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold flex items-center gap-2 text-white">
              <CalendarIcon className="w-6 h-6 text-white" />
              Calendar
            </h1>
            <div className="flex items-center gap-2">
              <button
                onClick={previousMonth}
                className="btn-icon"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="text-lg font-semibold min-w-[200px] text-center">
                {format(currentDate, 'MMMM yyyy')}
              </span>
              <button
                onClick={nextMonth}
                className="btn-icon"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            <button className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4 text-dark-bg" />
              <span className="text-dark-bg">New Event</span>
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="card overflow-hidden">
            {/* Day Names */}
            <div className="grid grid-cols-7 border-b border-dark-border">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div
                  key={day}
                  className="p-3 text-center text-xs font-semibold text-dark-text-tertiary"
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Days Grid */}
            <div className="grid grid-cols-7">
              {daysInMonth.map((day) => {
                const dayEvents = getEventsForDay(day)
                const isSelected = isSameDay(day, selectedDate)
                const isCurrentDay = isToday(day)

                return (
                  <button
                    key={day.toString()}
                    onClick={() => setSelectedDate(day)}
                    className={`min-h-[100px] p-2 border-r border-b border-dark-border hover:bg-dark-hover transition-colors ${
                      !isSameMonth(day, currentDate) ? 'opacity-30' : ''
                    } ${isSelected ? 'bg-dark-hover ring-1 ring-white' : ''}`}
                  >
                    <div className="flex flex-col h-full">
                      <span
                        className={`text-sm font-medium mb-1 w-7 h-7 flex items-center justify-center rounded-full ${
                          isCurrentDay
                            ? 'bg-white text-dark-bg'
                            : isSelected
                            ? 'text-white'
                            : 'text-dark-text-primary'
                        }`}
                      >
                        {format(day, 'd')}
                      </span>
                      <div className="flex-1 space-y-1 overflow-y-auto">
                        {dayEvents.slice(0, 2).map((event) => (
                          <div
                            key={event.id}
                            className={`text-xs px-1.5 py-0.5 rounded ${getEventTypeColor(
                              event.type
                            )} text-white truncate`}
                          >
                            {event.title}
                          </div>
                        ))}
                        {dayEvents.length > 2 && (
                          <div className="text-xs text-dark-text-tertiary">
                            +{dayEvents.length - 2} more
                          </div>
                        )}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Event Details Sidebar */}
      <div className="lg:w-80 border-t lg:border-t-0 lg:border-l border-dark-border bg-dark-surface p-6 overflow-y-auto">
        <h2 className="text-lg font-semibold mb-4">
          {format(selectedDate, 'EEEE, MMMM d')}
        </h2>

        {selectedDayEvents.length === 0 ? (
          <div className="text-center py-8 text-dark-text-tertiary">
            <CalendarIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No events scheduled</p>
          </div>
        ) : (
          <div className="space-y-3">
            {selectedDayEvents.map((event) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="card p-4 space-y-2"
              >
                <div className="flex items-start gap-2">
                  <div
                    className={`${getEventTypeColor(
                      event.type
                    )} p-1.5 rounded-ai text-white`}
                  >
                    {getEventTypeIcon(event.type)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-sm">{event.title}</h3>
                    {event.description && (
                      <p className="text-xs text-dark-text-secondary mt-1">
                        {event.description}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-xs text-dark-text-tertiary">
                  {format(event.startTime, 'h:mm a')} -{' '}
                  {format(event.endTime, 'h:mm a')}
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs px-2 py-1 rounded-ai-sm ${
                      event.status === 'completed'
                        ? 'bg-green-500/20 text-green-500'
                        : 'bg-yellow-500/20 text-yellow-500'
                    }`}
                  >
                    {event.status}
                  </span>
                  <span className="text-xs text-dark-text-tertiary capitalize">
                    {event.type}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
