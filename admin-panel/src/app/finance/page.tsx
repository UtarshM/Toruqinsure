import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Wallet, ArrowUpCircle, ArrowDownCircle, Search, Filter } from 'lucide-react'

export default function FinancePage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Finance & Ledger</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor income, expenses, and transaction history.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
          Add Transaction
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4">
            <Wallet size={24} />
          </div>
          <p className="text-sm font-medium text-gray-500">Total Balance</p>
          <h3 className="text-2xl font-bold text-gray-900 mt-1">₹12,45,000</h3>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="w-12 h-12 bg-green-50 text-green-600 rounded-xl flex items-center justify-center mb-4">
            <ArrowUpCircle size={24} />
          </div>
          <p className="text-sm font-medium text-gray-500">Monthly Income</p>
          <h3 className="text-2xl font-bold text-green-600 mt-1">+₹4,20,000</h3>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="w-12 h-12 bg-red-50 text-red-600 rounded-xl flex items-center justify-center mb-4">
            <ArrowDownCircle size={24} />
          </div>
          <p className="text-sm font-medium text-gray-500">Monthly Expenses</p>
          <h3 className="text-2xl font-bold text-red-600 mt-1">-₹85,000</h3>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="mt-8 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-50 flex items-center justify-between">
          <h3 className="font-bold text-gray-900">Recent Transactions</h3>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input 
                type="text" 
                placeholder="Search transactions..." 
                className="pl-10 pr-4 py-2 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none w-64"
              />
            </div>
            <button className="p-2 bg-gray-50 text-gray-600 rounded-xl hover:bg-gray-100">
              <Filter size={18} />
            </button>
          </div>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50/50 text-left">
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Transaction ID</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Category</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Amount</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Status</th>
              <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">#TRX-00{i}45</td>
                <td className="px-6 py-4">
                  <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold">
                    Policy Premium
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-bold text-gray-900">₹45,000</td>
                <td className="px-6 py-4">
                  <span className="flex items-center gap-1.5 text-green-600 text-sm font-medium">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-600"></span>
                    Completed
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">19 Apr 2026</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  )
}
