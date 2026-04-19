"use client"
import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const MENU_ITEMS = [
  { name: 'Dashboard', href: '/' },
  { name: 'Leads', href: '/leads' },
  { name: 'CRM', href: '/crm' },
  { name: 'Policies', href: '/policies' },
  { name: 'Claims', href: '/claims' },
  { name: 'Loans & Finance', href: '/loans' },
  { name: 'RTO Work', href: '/rto' },
  { name: 'Fitness', href: '/fitness' },
  { name: 'Follow-ups', href: '/follow-ups' },
  { name: 'User Management', href: '/users' },
  { name: 'Roles & Permissions', href: '/roles' },
  { name: 'Settings', href: '/settings' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0 z-30">
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-xl">
            T
          </div>
          <span className="text-xl font-bold text-gray-900 tracking-tight">Torque</span>
        </div>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        {MENU_ITEMS.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                isActive 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-blue-600'
              }`}
            >
              {item.name}
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-gray-100">
        <button className="w-full flex items-center gap-3 px-4 py-3 text-sm font-semibold text-red-600 hover:bg-red-50 rounded-xl transition-all">
          Logout
        </button>
      </div>
    </div>
  )
}
