import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const rto = await prisma.rTOWork.findMany({
      orderBy: { createdAt: 'desc' },
      include: { lead: { select: { clientName: true } } }
    })
    return NextResponse.json(rto)
  } catch (error) {
    console.error('RTO GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const data = await req.json()
    const rto = await prisma.rTOWork.create({
      data: {
        leadId: data.lead_id,
        assignedTo: data.assigned_to,
        customerName: data.customer_name,
        vehicleNumber: data.vehicle_number,
        workType: data.work_type,
        status: data.status || 'pending',
        rtoOffice: data.rto_office,
        fees: data.fees,
        dueDate: data.due_date ? new Date(data.due_date) : null
      }
    })
    return NextResponse.json(rto)
  } catch (error) {
    console.error('RTO POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
