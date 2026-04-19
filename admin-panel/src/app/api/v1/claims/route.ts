import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const status = searchParams.get('status')
    
    const where: any = {}
    if (status && status !== 'all') {
      where.status = status
    }

    const claims = await prisma.claim.findMany({
      where,
      orderBy: { filedDate: 'desc' },
      include: {
        lead: { select: { clientName: true } },
        policy: { select: { policyNumber: true } }
      }
    })

    return NextResponse.json(claims)
  } catch (error) {
    console.error('Claims GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const claim = await prisma.claim.create({
      data: {
        policyId: body.policy_id,
        leadId: body.lead_id,
        assignedTo: body.assigned_to,
        customerName: body.customer_name,
        policyNumber: body.policy_number,
        vehicleNumber: body.vehicle_number,
        claimType: body.claim_type,
        claimAmount: body.claim_amount,
        incidentDate: body.incident_date ? new Date(body.incident_date) : null,
        status: 'filed'
      }
    })
    return NextResponse.json(claim)
  } catch (error) {
    console.error('Claim POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
