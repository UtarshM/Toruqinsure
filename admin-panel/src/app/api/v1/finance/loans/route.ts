import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url)
    const status = searchParams.get('status')
    
    const where: any = {}
    if (status && status !== 'all') where.status = status

    const loans = await prisma.loan.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        lead: { select: { clientName: true } },
        assignee: { select: { fullName: true } }
      }
    })

    return NextResponse.json(loans)
  } catch (error) {
    console.error('Loans GET Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const loan = await prisma.loan.create({
      data: {
        leadId: body.lead_id,
        assignedTo: body.assigned_to,
        customerName: body.customer_name,
        loanType: body.loan_type,
        amount: body.amount,
        tenureMonths: body.tenure_months,
        interestRate: body.interest_rate,
        status: body.status || 'applied',
        bankName: body.bank_name
      }
    })
    return NextResponse.json(loan)
  } catch (error) {
    console.error('Loan POST Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
