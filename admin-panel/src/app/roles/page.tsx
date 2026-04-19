"use client"
import React, { useState, useEffect } from 'react'
import AdminLayout from '@/components/layout/AdminLayout'
import { 
  Shield, 
  Users, 
  CheckCircle2, 
  Circle, 
  Save, 
  ChevronRight,
  Search,
  Lock,
  ChevronDown
} from 'lucide-react'

export default function RolesPage() {
  const [roles, setRoles] = useState<any[]>([])
  const [permissions, setPermissions] = useState<any[]>([])
  const [selectedRole, setSelectedRole] = useState<any>(null)
  const [rolePermissions, setRolePermissions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedGroups, setExpandedGroups] = useState<string[]>([])

  useEffect(() => {
    fetchInitialData()
  }, [])

  const fetchInitialData = async () => {
    try {
      const [rolesRes, permsRes] = await Promise.all([
        fetch('/api/v1/roles'),
        fetch('/api/v1/permissions')
      ])
      const rolesData = await rolesRes.json()
      const permsData = await permsRes.json()
      
      setRoles(rolesData)
      setPermissions(permsData)
      
      if (rolesData.length > 0) {
        handleSelectRole(rolesData[0])
      }
    } catch (error) {
      console.error('Failed to fetch roles/permissions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectRole = async (role: any) => {
    setSelectedRole(role)
    setIsLoading(true)
    try {
      const res = await fetch(`/api/v1/roles/${role.id}`)
      const data = await res.json()
      setRolePermissions(data.permissions.map((p: any) => p.id))
    } catch (error) {
      console.error('Failed to fetch role permissions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const togglePermission = (id: string) => {
    setRolePermissions(prev => 
      prev.includes(id) ? prev.filter(pid => pid !== id) : [...prev, id]
    )
  }

  const handleSave = async () => {
    if (!selectedRole) return
    setIsSaving(true)
    try {
      const res = await fetch(`/api/v1/roles/${selectedRole.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ permissionIds: rolePermissions })
      })
      if (res.ok) {
        alert('Permissions updated successfully!')
      }
    } catch (error) {
      console.error('Failed to save permissions:', error)
      alert('Failed to save changes')
    } finally {
      setIsSaving(false)
    }
  }

  // Group permissions by module
  const groups: Record<string, any[]> = {}
  permissions.forEach(p => {
    const groupName = p.name.split('.')[0]
    if (!groups[groupName]) groups[groupName] = []
    groups[groupName].push(p)
  })

  const filteredGroups = Object.keys(groups).filter(group => 
    group.toLowerCase().includes(searchQuery.toLowerCase()) ||
    groups[group].some(p => p.name.toLowerCase().includes(searchQuery.toLowerCase()))
  )

  const toggleGroup = (group: string) => {
    setExpandedGroups(prev => 
      prev.includes(group) ? prev.filter(g => g !== group) : [...prev, group]
    )
  }

  const toggleAllInGroup = (group: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const groupPermIds = groups[group].map(p => p.id)
    const allSelected = groupPermIds.every(id => rolePermissions.includes(id))
    
    if (allSelected) {
      setRolePermissions(prev => prev.filter(id => !groupPermIds.includes(id)))
    } else {
      setRolePermissions(prev => [...new Set([...prev, ...groupPermIds])])
    }
  }

  if (isLoading && roles.length === 0) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </AdminLayout>
    )
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Roles & Permissions</h1>
            <p className="text-gray-500 mt-1">Configure role-based access control for your organization.</p>
          </div>
          <button 
            onClick={handleSave}
            disabled={isSaving || !selectedRole}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 disabled:opacity-50"
          >
            {isSaving ? 'Saving...' : <><Save size={18} /> Save Changes</>}
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Roles List */}
          <div className="w-full lg:w-80 space-y-4">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest px-2">Select Role</h3>
            <div className="space-y-2">
              {roles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => handleSelectRole(role)}
                  className={`w-full flex items-center justify-between p-4 rounded-2xl border transition-all ${
                    selectedRole?.id === role.id
                      ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-100'
                      : 'bg-white border-gray-100 text-gray-700 hover:border-blue-200'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Shield size={20} className={selectedRole?.id === role.id ? 'text-blue-100' : 'text-blue-600'} />
                    <div className="text-left">
                      <p className="text-sm font-bold">{role.name}</p>
                      <p className={`text-[10px] ${selectedRole?.id === role.id ? 'text-blue-100' : 'text-gray-400'}`}>
                        {role._count.users} Users Assigned
                      </p>
                    </div>
                  </div>
                  <ChevronRight size={16} className={selectedRole?.id === role.id ? 'text-blue-100' : 'text-gray-300'} />
                </button>
              ))}
            </div>
          </div>

          {/* Permissions Grid */}
          <div className="flex-1 space-y-6">
            <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex items-center gap-4">
              <Search className="text-gray-400" size={20} />
              <input 
                type="text" 
                placeholder="Search modules or permissions..." 
                className="flex-1 bg-transparent border-none outline-none text-sm"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="space-y-4">
              {filteredGroups.map((group) => {
                const isExpanded = expandedGroups.includes(group) || searchQuery !== ''
                const groupPerms = groups[group]
                const selectedInGroup = groupPerms.filter(p => rolePermissions.includes(p.id)).length
                
                return (
                  <div key={group} className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                    <div 
                      onClick={() => toggleGroup(group)}
                      className="p-6 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold uppercase">
                          {group.charAt(0)}
                        </div>
                        <div>
                          <h4 className="font-bold text-gray-900 capitalize">{group} Management</h4>
                          <p className="text-xs text-gray-500 mt-0.5">
                            {selectedInGroup} of {groupPerms.length} permissions active
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <button 
                          onClick={(e) => toggleAllInGroup(group, e)}
                          className="text-[10px] font-bold text-blue-600 hover:text-blue-700 uppercase tracking-widest px-3 py-1 bg-blue-50 rounded-lg"
                        >
                          {selectedInGroup === groupPerms.length ? 'Deselect All' : 'Select All'}
                        </button>
                        <ChevronDown 
                          size={20} 
                          className={`text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
                        />
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-6 pb-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 border-t border-gray-50 pt-6">
                        {groupPerms.map((p) => {
                          const isActive = rolePermissions.includes(p.id)
                          return (
                            <div 
                              key={p.id}
                              onClick={() => togglePermission(p.id)}
                              className={`flex items-center gap-3 p-3 rounded-xl border transition-all cursor-pointer ${
                                isActive 
                                  ? 'bg-blue-50/50 border-blue-200 shadow-sm' 
                                  : 'bg-white border-gray-50 hover:border-gray-200'
                              }`}
                            >
                              {isActive ? (
                                <CheckCircle2 size={18} className="text-blue-600 shrink-0" />
                              ) : (
                                <Circle size={18} className="text-gray-300 shrink-0" />
                              )}
                              <div className="min-w-0">
                                <p className={`text-sm font-bold truncate ${isActive ? 'text-blue-900' : 'text-gray-700'}`}>
                                  {p.name.split('.')[1].replace(/_/g, ' ')}
                                </p>
                                <p className="text-[10px] text-gray-400 truncate mt-0.5">{p.name}</p>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}
