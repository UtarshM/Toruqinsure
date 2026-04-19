"use client"
import AdminLayout from '@/components/layout/AdminLayout'
import { 
  Users2, 
  ShieldCheck, 
  TrendingUp, 
  Clock, 
  ArrowUpRight, 
  ArrowDownRight,
  Plus
} from 'lucide-react'

const STAT_CARDS = [
  { name: 'Total Leads', value: '2,845', change: '+12.5%', isUp: true, icon: Users2, color: 'text-blue-600', bg: 'bg-blue-100' },
  { name: 'Active Policies', value: '1,240', change: '+5.2%', isUp: true, icon: ShieldCheck, color: 'text-green-600', bg: 'bg-green-100' },
  { name: 'Pending Claims', value: '45', change: '-2.1%', isUp: false, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-100' },
  { name: 'Monthly Revenue', value: '₹14.2L', change: '+18.4%', isUp: true, icon: TrendingUp, color: 'text-purple-600', bg: 'bg-purple-100' },
]

export default function DashboardPage() {
  return (
    <AdminLayout>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back, Admin. Here's what's happening today.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl text-sm font-semibold hover:bg-gray-50 transition-all">
            Download Report
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold hover:bg-blue-700 transition-all shadow-md shadow-blue-200">
            <Plus size={18} />
            New Lead
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {STAT_CARDS.map((stat) => (
          <div key={stat.name} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 rounded-xl ${stat.bg} ${stat.color}`}>
                <stat.icon size={24} />
              </div>
              <div className={`flex items-center gap-1 text-sm font-bold ${stat.isUp ? 'text-green-600' : 'text-red-600'}`}>
                {stat.change}
                {stat.isUp ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{stat.name}</p>
              <h3 className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Activity */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-50 flex items-center justify-between">
            <h2 className="text-lg font-bold text-gray-900">Recent Leads</h2>
            <button className="text-sm font-semibold text-blue-600 hover:text-blue-700">View All</button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50/50">
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Customer</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase tracking-wider">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {[
                  { name: 'Rahul Sharma', email: 'rahul@example.com', type: 'Car Insurance', status: 'New', date: '10 mins ago' },
                  { name: 'Priya Patel', email: 'priya@example.com', type: 'Health Insurance', status: 'Contacted', date: '1 hour ago' },
                  { name: 'Amit Kumar', email: 'amit@example.com', type: 'Life Insurance', status: 'Quote Sent', date: '3 hours ago' },
                  { name: 'Sneha Gupta', email: 'sneha@example.com', type: 'Two Wheeler', status: 'New', date: '5 hours ago' },
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50/50 transition-colors cursor-pointer">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-bold text-gray-900">{row.name}</div>
                        <div className="text-xs text-gray-500">{row.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{row.type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        row.status === 'New' ? 'bg-blue-100 text-blue-600' : 
                        row.status === 'Contacted' ? 'bg-amber-100 text-amber-600' :
                        'bg-green-100 text-green-600'
                      }`}>
                        {row.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{row.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Task List / Follow-ups */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-50">
            <h2 className="text-lg font-bold text-gray-900">Today's Tasks</h2>
          </div>
          <div className="p-6 space-y-6">
            {[
              { title: 'Call Rahul Sharma', time: '10:30 AM', priority: 'High' },
              { title: 'Approve Claim #4521', time: '12:00 PM', priority: 'Medium' },
              { title: 'Review Sales Report', time: '03:30 PM', priority: 'Low' },
              { title: 'Meeting with RTO Team', time: '05:00 PM', priority: 'High' },
            ].map((task, i) => (
              <div key={i} className="flex items-start gap-4 group">
                <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${
                  task.priority === 'High' ? 'bg-red-500' :
                  task.priority === 'Medium' ? 'bg-amber-500' :
                  'bg-blue-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors cursor-pointer">{task.title}</p>
                  <p className="text-xs text-gray-500 mt-1">{task.time}</p>
                </div>
                <button className="text-gray-400 hover:text-blue-600 opacity-0 group-hover:opacity-100 transition-all">
                  <Plus size={16} />
                </button>
              </div>
            ))}
          </div>
          <div className="p-6 pt-0">
            <button className="w-full py-2 bg-gray-50 text-gray-600 text-sm font-semibold rounded-xl hover:bg-gray-100 transition-all">
              View All Tasks
            </button>
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
