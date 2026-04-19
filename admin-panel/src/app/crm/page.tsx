import React from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { Users, UserPlus, Mail, Phone, MapPin, MoreVertical } from 'lucide-react'

export default function CRMPage() {
  return (
    <AdminLayout>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">CRM & Clients</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your customer relationships and historical data.</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all">
          <UserPlus size={18} />
          Add Client
        </button>
      </div>

      {/* Grid of Client Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow relative group">
            <button className="absolute top-4 right-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity">
              <MoreVertical size={20} />
            </button>
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl flex items-center justify-center text-xl font-bold">
                {['A', 'K', 'M', 'S', 'V', 'R'][i-1]}
              </div>
              <div>
                <h4 className="font-bold text-gray-900 text-lg">
                  {['Amit Kumar', 'Karan Singh', 'Meera Iyer', 'Suresh Patel', 'Vijay Gupta', 'Rohan Das'][i-1]}
                </h4>
                <p className="text-xs font-semibold text-blue-600 uppercase tracking-widest mt-0.5">Premium Client</p>
              </div>
            </div>
            
            <div className="mt-6 space-y-3">
              <div className="flex items-center gap-3 text-gray-500">
                <Mail size={16} />
                <span className="text-sm">client{i}@example.com</span>
              </div>
              <div className="flex items-center gap-3 text-gray-500">
                <Phone size={16} />
                <span className="text-sm">+91 98234 5678{i}</span>
              </div>
              <div className="flex items-center gap-3 text-gray-500">
                <MapPin size={16} />
                <span className="text-sm">Ahmedabad, Gujarat</span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-50 flex items-center justify-between">
              <div>
                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Total Policies</p>
                <p className="text-sm font-bold text-gray-900">{i + 1}</p>
              </div>
              <button className="text-blue-600 text-sm font-bold hover:underline transition-all">
                Full Profile
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="mt-8 flex items-center justify-center gap-2">
        <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-100 text-gray-400 font-bold hover:bg-gray-50 disabled:opacity-50" disabled>1</button>
        <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-100 text-gray-600 font-bold hover:bg-gray-50">2</button>
        <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-100 text-gray-600 font-bold hover:bg-gray-50">3</button>
        <span className="mx-2 text-gray-400 text-sm font-bold">...</span>
        <button className="w-10 h-10 flex items-center justify-center rounded-xl bg-white border border-gray-100 text-gray-600 font-bold hover:bg-gray-50">12</button>
      </div>
    </AdminLayout>
  )
}
