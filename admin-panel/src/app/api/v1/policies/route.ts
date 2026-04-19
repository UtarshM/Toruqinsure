import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const status = searchParams.get('status')
    
    const where: any = {}
    if (status && status !== 'all') where.status = status

    const policies = await prisma.policy.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        lead: { select: { clientName: true } }
      }
    })

    return NextResponse.json(policies)
  } catch (error) {
    console.error('Policies GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const policy = await prisma.policy.create({
      data: {
        leadId: body.lead_id,
        policyNumber: body.policy_number,
        provider: body.provider,
        type: body.type,
        premiumAmount: body.premium_amount,
        status: body.status || 'Active',
        startDate: new Date(body.start_date),
        endDate: new Date(body.end_date)
      }
    })
    return NextResponse.json(policy)
  } catch (error) {
    console.error('Policy POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
