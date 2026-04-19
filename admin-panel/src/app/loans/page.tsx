import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Landmark, FileCheck, ArrowRight, User } from 'lucide-react'

export default function LoansPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Loans & Finance</h1>
          <p className="text-sm text-gray-500 mt-1">Manage vehicle and personal loan applications.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
          New Loan Application
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
        {/* Loan Queue */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-bold text-gray-900 px-1">Active Applications</h3>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center justify-between hover:border-blue-200 transition-all group">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gray-50 text-gray-400 rounded-xl flex items-center justify-center group-hover:bg-blue-50 group-hover:text-blue-500 transition-colors">
                  <User size={24} />
                </div>
                <div>
                  <h4 className="font-bold text-gray-900">Rahul Sharma</h4>
                  <p className="text-xs text-gray-500 font-medium">Vehicle Loan · ₹4,50,000</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <span className="px-2.5 py-1 bg-yellow-50 text-yellow-700 rounded-lg text-[10px] font-bold uppercase tracking-wider">
                    Processing
                  </span>
                  <p className="text-[10px] text-gray-400 mt-1 font-medium">Applied 2 days ago</p>
                </div>
                <button className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center text-gray-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
                  <ArrowRight size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Quick Stats & Banks */}
        <div className="space-y-6">
          <div className="bg-blue-600 p-6 rounded-2xl text-white shadow-lg shadow-blue-200">
            <h4 className="font-bold text-lg">Loan Approvals</h4>
            <p className="text-blue-100 text-sm mt-1">Current approval rate is 78% this month.</p>
            <div className="mt-6 flex items-end gap-2">
              <span className="text-4xl font-bold">24</span>
              <span className="text-blue-200 text-sm mb-1 pb-1">Approvals</span>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h4 className="font-bold text-gray-900 mb-4">Partner Banks</h4>
            <div className="space-y-4">
              {['HDFC Bank', 'ICICI Bank', 'SBI Finance', 'Axis Bank'].map((bank) => (
                <div key={bank} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 cursor-pointer transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center text-blue-600 shadow-sm">
                      <Landmark size={16} />
                    </div>
                    <span className="text-sm font-semibold text-gray-700">{bank}</span>
                  </div>
                  <FileCheck size={16} className="text-green-500" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
