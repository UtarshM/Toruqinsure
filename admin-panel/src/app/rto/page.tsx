import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Car, FileText, CheckCircle, Clock, AlertTriangle, Search } from 'lucide-react'

export default function RTOPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">RTO Work Management</h1>
          <p className="text-sm text-gray-500 mt-1">Track vehicle transfers, NOCs, and registration updates.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
          New RTO Task
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider">Pending Tasks</p>
            <Clock className="text-orange-500" size={20} />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">12</h3>
          <p className="text-xs text-gray-400 mt-2">4 tasks overdue</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider">In Progress</p>
            <Car className="text-blue-500" size={20} />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">28</h3>
          <p className="text-xs text-gray-400 mt-2">8 tasks at RTO office</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-wider">Completed</p>
            <CheckCircle className="text-green-500" size={20} />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mt-2">156</h3>
          <p className="text-xs text-gray-400 mt-2">Last 30 days</p>
        </div>
      </div>

      <div className="mt-8 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-50 flex items-center justify-between">
          <h3 className="font-bold text-gray-900">Active RTO Tasks</h3>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search by Vehicle No..." 
              className="pl-10 pr-4 py-2 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none w-64"
            />
          </div>
        </div>
        <table className="w-full text-left">
          <thead>
            <tr className="bg-gray-50/50">
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Vehicle No</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Service Type</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Customer</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Status</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {[1, 2, 3].map((i) => (
              <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 text-sm font-bold text-gray-900">GJ-01-XX-900{i}</td>
                <td className="px-6 py-4 text-sm text-gray-600">Ownership Transfer</td>
                <td className="px-6 py-4 text-sm text-gray-600">Karan Patel</td>
                <td className="px-6 py-4">
                  <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold">
                    At RTO Office
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="text-blue-600 hover:text-blue-700 text-sm font-bold">Update</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  )
}
