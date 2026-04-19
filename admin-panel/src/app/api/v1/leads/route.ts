import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const status = searchParams.get('status')
    const search = searchParams.get('search')
    const limit = parseInt(searchParams.get('limit') || '50')
    const offset = parseInt(searchParams.get('offset') || '0')

    const where: any = {}
    if (status && status !== 'all') {
      where.status = status
    }
    if (search) {
      where.OR = [
        { clientName: { contains: search, mode: 'insensitive' } },
        { clientPhone: { contains: search, mode: 'insensitive' } }
      ]
    }

    const [leads, total] = await Promise.all([
      prisma.lead.findMany({
        where,
        take: limit,
        skip: offset,
        orderBy: { createdAt: 'desc' },
        include: {
          assignee: {
            select: { fullName: true }
          }
        }
      }),
      prisma.lead.count({ where })
    ])

    return NextResponse.json(leads)
  } catch (error) {
    console.error('Leads GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const lead = await prisma.lead.create({
      data: {
        clientName: body.client_name,
        clientEmail: body.client_email,
        clientPhone: body.client_phone,
        status: body.status || 'New',
        assignedTo: body.assigned_to
      }
    })
    return NextResponse.json(lead)
  } catch (error) {
    console.error('Lead POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
