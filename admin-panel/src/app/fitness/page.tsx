import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Briefcase, AlertTriangle, Calendar, Search, MoreHorizontal } from 'lucide-react'

export default function FitnessPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Fitness Certificates</h1>
          <p className="text-sm text-gray-500 mt-1">Manage and track commercial vehicle fitness renewals.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
          New Fitness Task
        </button>
      </div>

      {/* Expiry Alerts */}
      <div className="mt-8 bg-red-50 border border-red-100 p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-red-100 text-red-600 rounded-xl flex items-center justify-center">
            <AlertTriangle size={24} />
          </div>
          <div>
            <h3 className="font-bold text-red-900">8 Certificates Expiring Soon</h3>
            <p className="text-sm text-red-700">These vehicles need fitness inspection within the next 7 days.</p>
          </div>
        </div>
        <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 transition-colors">
          View All
        </button>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative group">
            <div className="flex items-center justify-between mb-4">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <Briefcase size={20} />
              </div>
              <button className="text-gray-400 hover:text-gray-600"><MoreHorizontal size={20} /></button>
            </div>
            <h4 className="text-lg font-bold text-gray-900">Truck GJ-05-YT-220{i}</h4>
            <p className="text-sm text-gray-500 font-medium mt-1">Owner: Rajesh Roadways</p>
            
            <div className="mt-6 flex items-center justify-between">
              <div>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Expiry Date</p>
                <div className="flex items-center gap-1.5 mt-1 text-gray-900 font-bold text-sm">
                  <Calendar size={14} className="text-blue-500" />
                  22 Apr 2026
                </div>
              </div>
              <div className="text-right">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Days Left</p>
                <p className="text-sm font-bold text-red-600 mt-1">3 Days</p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-50 flex items-center gap-2">
              <button className="flex-1 py-2 bg-gray-50 text-gray-600 text-xs font-bold rounded-lg hover:bg-gray-100">Ignore</button>
              <button className="flex-1 py-2 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700">Create Task</button>
            </div>
          </div>
        ))}
      </div>
    </AdminLayout>
  )
}
