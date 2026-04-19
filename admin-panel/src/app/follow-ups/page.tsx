import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Calendar, Clock, Bell, User, CheckCircle2, ChevronRight } from 'lucide-react'

export default function FollowupsPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Follow-ups & Tasks</h1>
          <p className="text-sm text-gray-500 mt-1">Schedule and monitor client callbacks and reminders.</p>
        </div>
        <div className="flex items-center gap-2">
           <button className="px-4 py-2 bg-white border border-gray-200 text-gray-600 rounded-xl text-sm font-semibold hover:bg-gray-50">
            Calendar View
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all shadow-md shadow-blue-100">
            Schedule Follow-up
          </button>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Filters */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h3 className="font-bold text-gray-900 mb-4">Filters</h3>
            <div className="space-y-2">
              {['Today', 'Tomorrow', 'This Week', 'Overdue', 'Completed'].map((filter) => (
                <button 
                  key={filter} 
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                    filter === 'Today' ? 'bg-blue-50 text-blue-600' : 'text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  {filter}
                  <span className={`text-[10px] px-2 py-0.5 rounded-full ${
                    filter === 'Today' ? 'bg-blue-100' : 'bg-gray-100'
                  }`}>
                    {filter === 'Today' ? '12' : '4'}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-600 to-blue-700 p-6 rounded-2xl text-white shadow-xl shadow-blue-100">
            <Bell size={24} className="mb-4 text-blue-200" />
            <h4 className="font-bold text-lg leading-tight">Smart Reminders</h4>
            <p className="text-blue-100 text-xs mt-2 leading-relaxed">
              We'll automatically remind your team via Push Notifications on the Mobile App.
            </p>
          </div>
        </div>

        {/* Follow-up List */}
        <div className="lg:col-span-3 space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between hover:shadow-md transition-all group">
              <div className="flex items-center gap-6 flex-1">
                <div className="w-14 h-14 bg-gray-50 text-gray-400 rounded-2xl flex items-center justify-center group-hover:bg-blue-50 group-hover:text-blue-600 transition-all">
                  <User size={28} />
                </div>
                <div>
                  <div className="flex items-center gap-3">
                    <h4 className="font-bold text-gray-900 text-lg">Prashant Varma</h4>
                    <span className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-[10px] font-bold uppercase tracking-widest">Phone Call</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1 font-medium italic">"Interested in Commercial truck insurance, call at 11 AM"</p>
                  <div className="flex items-center gap-6 mt-3">
                    <div className="flex items-center gap-1.5 text-xs font-bold text-gray-400">
                      <Clock size={14} className="text-blue-500" />
                      11:30 AM
                    </div>
                    <div className="flex items-center gap-1.5 text-xs font-bold text-gray-400">
                      <Calendar size={14} className="text-blue-500" />
                      19 Apr 2026
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <button className="p-3 bg-green-50 text-green-600 rounded-xl hover:bg-green-100 transition-colors">
                  <CheckCircle2 size={20} />
                </button>
                <button className="p-3 bg-gray-50 text-gray-400 rounded-xl hover:bg-gray-100 transition-colors">
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </AdminLayout>
  )
}
