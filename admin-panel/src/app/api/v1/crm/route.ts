import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const customers = await prisma.customer.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        visits: { orderBy: { scheduledAt: 'desc' }, take: 5 }
      }
    })
    return NextResponse.json(customers)
  } catch (error) {
    console.error('CRM GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const customer = await prisma.customer.create({
      data: {
        leadId: body.lead_id,
        name: body.name,
        phone: body.phone,
        email: body.email,
        address: body.address,
        kycStatus: body.kyc_status || 'pending'
      }
    })
    return NextResponse.json(customer)
  } catch (error) {
    console.error('Customer POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
