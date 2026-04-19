import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const role = await prisma.role.findUnique({
      where: { id: params.id },
      include: {
        permissions: true
      }
    })
    
    if (!role) return NextResponse.json({ error: 'Role not found' }, { status: 404 })
    
    return NextResponse.json(role)
  } catch (error) {
    console.error('Role Detail GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await req.json()
    const { permissionIds } = body // Array of permission IDs

    const role = await prisma.role.update({
      where: { id: params.id },
      data: {
        permissions: {
          set: permissionIds.map((id: string) => ({ id }))
        }
      },
      include: {
        permissions: true
      }
    })

    return NextResponse.json(role)
  } catch (error) {
    console.error('Role Update PATCH Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
