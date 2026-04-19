import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { supabaseAdmin } from '@/lib/supabase-admin'

export async function GET(req: NextRequest) {
  try {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) return NextResponse.json({ error: 'Missing token' }, { status: 401 })
    
    const token = authHeader.split(' ')[1]
    const { data: { user }, error } = await supabaseAdmin.auth.getUser(token)
    
    if (error || !user) return NextResponse.json({ error: 'Invalid token' }, { status: 401 })

    // Fetch profile from Prisma
    const profile = await prisma.user.findUnique({
      where: { id: user.id },
      include: {
        role: {
          include: { permissions: true }
        }
      }
    })

    if (!profile) {
      // Find the Super Admin role for the initial admin
      let roleId = null
      if (user.email === 'admin@toque.com') {
        const adminRole = await prisma.role.findUnique({ where: { name: 'Super Admin' } })
        roleId = adminRole?.id
      } else {
        const defaultRole = await prisma.role.findUnique({ where: { name: 'Viewer' } })
        roleId = defaultRole?.id
      }

      // Auto-create profile if it doesn't exist (first login)
      const newProfile = await prisma.user.create({
        data: {
          id: user.id,
          email: user.email!,
          fullName: user.user_metadata?.full_name || user.email!.split('@')[0],
          isActive: true,
          roleId: roleId
        },
        include: {
          role: { include: { permissions: true } }
        }
      })
      return NextResponse.json({
        ...newProfile,
        full_name: newProfile.fullName,
        is_active: newProfile.isActive
      })
    }

    if (user.email === 'admin@toque.com' && !profile.roleId) {
      const adminRole = await prisma.role.findUnique({ where: { name: 'Super Admin' } })
      if (adminRole) {
        const updatedProfile = await prisma.user.update({
          where: { id: profile.id },
          data: { roleId: adminRole.id },
          include: {
            role: { include: { permissions: true } }
          }
        })
        return NextResponse.json({
          ...updatedProfile,
          full_name: updatedProfile.fullName,
          is_active: updatedProfile.isActive
        })
      }
    }

    return NextResponse.json({
      ...profile,
      full_name: profile.fullName,
      is_active: profile.isActive
    })
  } catch (error) {
    console.error('Auth Me Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
