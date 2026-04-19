"use client"
import React, { useState, useEffect } from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import {
  UserPlus, Shield, Mail, Edit3, Trash2,
  CheckCircle2, XCircle, X, ChevronDown, ChevronUp, Lock
} from 'lucide-react'

const PERMISSION_GROUPS: Record<string, string[]> = {
  auth: ["auth.login","auth.logout","auth.pin_setup","auth.biometric_enable","auth.session_manage","auth.reset_access"],
  role: ["role.view","role.create","role.edit","role.delete","role.assign_permissions","role.manage_users"],
  lead: ["lead.view","lead.create","lead.edit","lead.delete","lead.assign","lead.import","lead.export","lead.change_status"],
  rate: ["rate.view","rate.calculate","rate.edit_rules","rate.manage_addons","rate.configure_tables","rate.export"],
  rto: ["rto.view","rto.create","rto.edit","rto.delete","rto.update_status","rto.track_payment"],
  fitness: ["fitness.view","fitness.create","fitness.edit","fitness.delete","fitness.update_status","fitness.track_payment"],
  claims: ["claims.view","claims.create","claims.edit","claims.delete","claims.update_status","claims.upload_documents"],
  accounts: ["accounts.view","accounts.create_entry","accounts.edit_entry","accounts.delete_entry","accounts.view_reports","accounts.export","accounts.manage_salary"],
  hr: ["hr.view","hr.create","hr.edit","hr.delete","hr.manage_attendance","hr.manage_leave","hr.view_performance"],
  loan: ["loan.view","loan.create","loan.edit","loan.delete","loan.update_status","loan.track_conversion"],
  crm: ["crm.view","crm.create","crm.edit","crm.delete","crm.manage_followups","crm.view_revenue"],
  visit: ["visit.view","visit.create","visit.edit","visit.delete","visit.track_location","visit.manage_followups"],
  data: ["data.view","data.create","data.edit","data.delete","data.approve_changes","data.manage_documents"],
  quotation: ["quotation.view","quotation.create","quotation.edit","quotation.delete","quotation.generate_pdf","quotation.share"],
  dashboard: ["dashboard.view_agent","dashboard.view_manager","dashboard.view_admin","dashboard.export"],
  notification: ["notification.view","notification.send","notification.manage","notification.configure"],
  template: ["template.view","template.create","template.edit","template.delete"],
  system: ["system.settings_manage","system.audit_logs_view"],
}

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [roles, setRoles] = useState<any[]>([])
  const [allPermissions, setAllPermissions] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Create user modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [createForm, setCreateForm] = useState({ fullName: '', email: '', password: '', roleId: '' })
  const [createError, setCreateError] = useState('')

  // Per-user permissions panel
  const [expandedUser, setExpandedUser] = useState<string | null>(null)
  const [userExtraPerms, setUserExtraPerms] = useState<Record<string, string[]>>({})
  const [savingPerms, setSavingPerms] = useState<string | null>(null)
  const [expandedGroups, setExpandedGroups] = useState<string[]>([])

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      const [usersRes, rolesRes, permsRes] = await Promise.all([
        fetch('/api/v1/users'),
        fetch('/api/v1/roles'),
        fetch('/api/v1/permissions')
      ])
      const [usersData, rolesData, permsData] = await Promise.all([
        usersRes.json(), rolesRes.json(), permsRes.json()
      ])
      setUsers(Array.isArray(usersData) ? usersData : [])
      setRoles(Array.isArray(rolesData) ? rolesData : [])
      setAllPermissions(Array.isArray(permsData) ? permsData : [])

      // Init extra perm state per user
      const permsMap: Record<string, string[]> = {}
      if (Array.isArray(usersData)) {
        usersData.forEach((u: any) => {
          permsMap[u.id] = (u.permissions || []).map((p: any) => p.id)
        })
      }
      setUserExtraPerms(permsMap)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateRole = async (userId: string, roleId: string) => {
    await fetch(`/api/v1/users/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roleId })
    })
    fetchData()
  }

  const handleToggleActive = async (userId: string, current: boolean) => {
    await fetch(`/api/v1/users/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ isActive: !current })
    })
    fetchData()
  }

  const handleDelete = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return
    await fetch(`/api/v1/users/${userId}`, { method: 'DELETE' })
    fetchData()
  }

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setCreateError('')
    try {
      const res = await fetch('/api/v1/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createForm)
      })
      const data = await res.json()
      if (!res.ok) {
        setCreateError(data.error || 'Failed to create user')
      } else {
        setShowCreateModal(false)
        setCreateForm({ fullName: '', email: '', password: '', roleId: '' })
        fetchData()
      }
    } catch {
      setCreateError('Network error. Please try again.')
    } finally {
      setCreating(false)
    }
  }

  const toggleExtraPerm = (userId: string, permId: string) => {
    setUserExtraPerms(prev => {
      const current = prev[userId] || []
      return {
        ...prev,
        [userId]: current.includes(permId)
          ? current.filter(id => id !== permId)
          : [...current, permId]
      }
    })
  }

  const saveExtraPerms = async (userId: string) => {
    setSavingPerms(userId)
    await fetch(`/api/v1/users/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ extraPermissionIds: userExtraPerms[userId] || [] })
    })
    setSavingPerms(null)
    fetchData()
  }

  const toggleGroup = (g: string) => {
    setExpandedGroups(prev => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g])
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
            <p className="text-sm text-gray-500 mt-1">Manage employee accounts, roles, and individual permissions.</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
          >
            <UserPlus size={18} />
            Add Employee
          </button>
        </div>

        {/* Users List */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center p-20 bg-white rounded-3xl border border-gray-100">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : users.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-20 bg-white rounded-3xl border border-gray-100 text-gray-400 text-center">
              <UserPlus size={48} className="mb-4 text-gray-200" />
              <p className="text-lg font-bold">No employees yet</p>
              <p className="text-sm mt-1">Click "Add Employee" to create your first team member.</p>
            </div>
          ) : users.map((user) => (
            <div key={user.id} className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
              {/* User Row */}
              <div className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="flex items-center gap-5">
                  <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl flex items-center justify-center font-bold text-xl shadow-lg">
                    {user.fullName?.charAt(0) ?? '?'}
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-gray-900">{user.fullName}</h4>
                    <div className="flex items-center gap-3 mt-1 flex-wrap">
                      <select
                        value={user.roleId || ''}
                        onChange={(e) => handleUpdateRole(user.id, e.target.value)}
                        className="bg-gray-50 border border-gray-200 text-xs font-semibold text-gray-600 rounded-lg px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
                      >
                        <option value="">No Role</option>
                        {roles.map(role => (
                          <option key={role.id} value={role.id}>{role.name}</option>
                        ))}
                      </select>
                      <button
                        onClick={() => handleToggleActive(user.id, user.isActive)}
                        className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-lg transition-all ${
                          user.isActive ? 'bg-green-50 text-green-600 hover:bg-green-100' : 'bg-red-50 text-red-500 hover:bg-red-100'
                        }`}
                      >
                        {user.isActive ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                        {user.isActive ? 'Active' : 'Inactive'}
                      </button>
                      {(user.permissions?.length > 0) && (
                        <span className="flex items-center gap-1 text-[10px] font-bold text-purple-600 bg-purple-50 px-2 py-1 rounded-lg">
                          <Lock size={10} />
                          +{user.permissions.length} extra permissions
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex flex-col md:flex-row items-start md:items-center gap-4 md:gap-8">
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Mail size={16} className="text-gray-400" />
                    <span>{user.email}</span>
                  </div>
                  <div className="flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-xl">
                    <Shield size={16} className="text-blue-600" />
                    <span className="text-blue-700 font-bold text-xs">{user.role?.name || 'No Role'}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setExpandedUser(expandedUser === user.id ? null : user.id)}
                    className="flex items-center gap-1 px-3 py-2 text-xs font-bold text-purple-600 bg-purple-50 hover:bg-purple-100 rounded-xl transition-all"
                  >
                    <Lock size={14} />
                    Extra Perms
                    {expandedUser === user.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                  </button>
                  <button
                    onClick={() => handleDelete(user.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              {/* Per-user Extra Permissions Panel */}
              {expandedUser === user.id && (
                <div className="border-t border-gray-100 bg-gray-50/50 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h5 className="font-bold text-gray-900 text-sm">Extra Permissions for {user.fullName}</h5>
                      <p className="text-xs text-gray-500 mt-0.5">
                        These are granted <strong>in addition to</strong> their role permissions.
                      </p>
                    </div>
                    <button
                      onClick={() => saveExtraPerms(user.id)}
                      disabled={savingPerms === user.id}
                      className="px-4 py-2 bg-purple-600 text-white rounded-xl text-xs font-bold hover:bg-purple-700 transition-all disabled:opacity-50"
                    >
                      {savingPerms === user.id ? 'Saving...' : 'Save'}
                    </button>
                  </div>

                  <div className="space-y-3">
                    {Object.entries(PERMISSION_GROUPS).map(([group, perms]) => {
                      const isOpen = expandedGroups.includes(group)
                      const permObjects = allPermissions.filter(p => perms.includes(p.name))
                      const selected = permObjects.filter(p => (userExtraPerms[user.id] || []).includes(p.id)).length

                      return (
                        <div key={group} className="bg-white rounded-2xl border border-gray-100">
                          <button
                            onClick={() => toggleGroup(group)}
                            className="w-full flex items-center justify-between p-4 text-left"
                          >
                            <span className="text-sm font-bold text-gray-700 capitalize">{group}</span>
                            <div className="flex items-center gap-3">
                              {selected > 0 && (
                                <span className="text-xs font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">
                                  {selected} active
                                </span>
                              )}
                              {isOpen ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                            </div>
                          </button>
                          {isOpen && (
                            <div className="px-4 pb-4 grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-2 border-t border-gray-50 pt-3">
                              {permObjects.map(p => {
                                const active = (userExtraPerms[user.id] || []).includes(p.id)
                                return (
                                  <button
                                    key={p.id}
                                    onClick={() => toggleExtraPerm(user.id, p.id)}
                                    className={`flex items-center gap-2 p-2 rounded-xl border text-left transition-all text-xs ${
                                      active
                                        ? 'bg-purple-50 border-purple-200 text-purple-700 font-bold'
                                        : 'bg-gray-50 border-gray-100 text-gray-500 hover:border-gray-200'
                                    }`}
                                  >
                                    <div className={`w-3 h-3 rounded-full flex-shrink-0 ${active ? 'bg-purple-500' : 'bg-gray-200'}`} />
                                    {p.name.split('.')[1]?.replace(/_/g, ' ')}
                                  </button>
                                )
                              })}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Create User Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Add New Employee</h2>
                <p className="text-sm text-gray-500 mt-1">Create a login account for your team member.</p>
              </div>
              <button
                onClick={() => { setShowCreateModal(false); setCreateError('') }}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-xl transition-all"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateUser} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1.5">Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Karan Mehra"
                  value={createForm.fullName}
                  onChange={e => setCreateForm(f => ({ ...f, fullName: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1.5">Email Address *</label>
                <input
                  type="email"
                  required
                  placeholder="karan@toque.in"
                  value={createForm.email}
                  onChange={e => setCreateForm(f => ({ ...f, email: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1.5">Password *</label>
                <input
                  type="password"
                  required
                  placeholder="Min 8 characters"
                  value={createForm.password}
                  onChange={e => setCreateForm(f => ({ ...f, password: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-700 mb-1.5">Assign Role</label>
                <select
                  value={createForm.roleId}
                  onChange={e => setCreateForm(f => ({ ...f, roleId: e.target.value }))}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                >
                  <option value="">Select a role (optional)</option>
                  {roles.map(role => (
                    <option key={role.id} value={role.id}>{role.name}</option>
                  ))}
                </select>
              </div>

              {createError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600 font-medium">
                  {createError}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => { setShowCreateModal(false); setCreateError('') }}
                  className="flex-1 px-4 py-3 border border-gray-200 text-gray-600 rounded-xl text-sm font-bold hover:bg-gray-50 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all disabled:opacity-50 shadow-lg shadow-blue-200"
                >
                  {creating ? 'Creating...' : 'Create Employee'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AdminLayout>
  )
}
