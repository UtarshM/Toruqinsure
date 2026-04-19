import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Shield, Search, FileText, Download, Filter } from 'lucide-react'

export default function PoliciesPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Policies & Insurance</h1>
          <p className="text-sm text-gray-500 mt-1">Manage active policies, renewals, and certificates.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-200 transition-all">
            Export Report
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
            Issue New Policy
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="mt-8 flex items-center justify-between gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
          <input 
            type="text" 
            placeholder="Search by Policy No, Vehicle No or Customer..." 
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none shadow-sm"
          />
        </div>
        <div className="flex items-center gap-2">
          <select className="px-4 py-2.5 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-600 outline-none">
            <option>All Types</option>
            <option>Motor</option>
            <option>Health</option>
            <option>Life</option>
          </select>
          <button className="p-2.5 bg-white border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50">
            <Filter size={18} />
          </button>
        </div>
      </div>

      {/* Policies Table */}
      <div className="mt-6 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-gray-50/50">
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Policy Info</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Customer</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Premium</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Expiry Date</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Status</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Docs</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center">
                      <Shield size={18} />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">POL-TIC-00{i}2</p>
                      <p className="text-[10px] text-gray-500 font-bold uppercase">Motor Insurance</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <p className="text-sm font-medium text-gray-900">Rajesh Malhotra</p>
                  <p className="text-xs text-gray-500">GJ-01-AB-1234</p>
                </td>
                <td className="px-6 py-4 text-sm font-bold text-gray-900">₹14,500</td>
                <td className="px-6 py-4">
                  <p className="text-sm text-gray-600">12 May 2027</p>
                  <p className="text-[10px] text-green-600 font-bold">Active</p>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-green-50 text-green-700 rounded-md text-[10px] font-bold">
                    VERIFIED
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="p-2 text-gray-400 hover:text-blue-600 transition-colors">
                    <Download size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  )
}
