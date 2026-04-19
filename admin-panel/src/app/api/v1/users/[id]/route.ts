import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const user = await prisma.user.findUnique({
      where: { id: params.id },
      include: {
        role: { include: { permissions: true } },
        permissions: true
      }
    })
    if (!user) return NextResponse.json({ error: 'User not found' }, { status: 404 })
    return NextResponse.json(user)
  } catch (error) {
    console.error('User GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await req.json()
    const { roleId, isActive, extraPermissionIds } = body

    const user = await prisma.user.update({
      where: { id: params.id },
      data: {
        ...(roleId !== undefined && { roleId: roleId || null }),
        ...(isActive !== undefined && { isActive }),
        ...(extraPermissionIds !== undefined && {
          permissions: {
            set: extraPermissionIds.map((id: string) => ({ id }))
          }
        })
      },
      include: {
        role: { select: { id: true, name: true } },
        permissions: { select: { id: true, name: true } }
      }
    })

    return NextResponse.json(user)
  } catch (error) {
    console.error('User PATCH Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.user.delete({ where: { id: params.id } })
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('User DELETE Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
