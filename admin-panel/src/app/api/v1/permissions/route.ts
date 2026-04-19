import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET() {
  try {
    const permissions = await prisma.permission.findMany({
      orderBy: { name: 'asc' }
    })
    return NextResponse.json(permissions)
  } catch (error) {
    console.error('Permissions GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
