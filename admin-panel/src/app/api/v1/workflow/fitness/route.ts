import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const fitness = await prisma.fitnessWork.findMany({
      orderBy: { createdAt: 'desc' },
      include: { lead: { select: { clientName: true } } }
    })
    return NextResponse.json(fitness)
  } catch (error) {
    console.error('Fitness GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const data = await req.json()
    const fitness = await prisma.fitnessWork.create({
      data: {
        leadId: data.lead_id,
        assignedTo: data.assigned_to,
        customerName: data.customer_name,
        vehicleNumber: data.vehicle_number,
        status: data.status || 'pending',
        testDate: data.test_date ? new Date(data.test_date) : null,
        fees: data.fees
      }
    })
    return NextResponse.json(fitness)
  } catch (error) {
    console.error('Fitness POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
