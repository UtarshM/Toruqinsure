import { NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { format } from 'date-fns'

export async function GET() {
  try {
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    // Aggregate stats in parallel
    const [
      totalLeads,
      newLeadsToday,
      totalPolicies,
      activePolicies,
      totalQuotations,
      totalCalls,
      pendingFollowups,
      overdueFollowups,
      activeClaims,
      pendingRto,
      pendingFitness,
      activeLoans,
      totalCustomers,
      todayVisits
    ] = await Promise.all([
      prisma.lead.count(),
      prisma.lead.count({ where: { createdAt: { gte: today } } }),
      prisma.policy.count(),
      prisma.policy.count({ where: { status: 'Active' } }),
      prisma.quotation.count(),
      prisma.call.count(),
      prisma.followUp.count({ where: { status: 'pending' } }),
      prisma.followUp.count({ where: { isOverdue: true } }),
      prisma.claim.count({ where: { status: { in: ['filed', 'under_review', 'approved'] } } }),
      prisma.rTOWork.count({ where: { status: 'pending' } }),
      prisma.fitnessWork.count({ where: { status: 'pending' } }),
      prisma.loan.count({ where: { status: { in: ['applied', 'under_review', 'approved', 'disbursed'] } } }),
      prisma.customer.count(),
      prisma.visit.count({ where: { scheduledAt: { gte: today } } })
    ])

    return NextResponse.json({
      total_leads: totalLeads,
      new_leads_today: newLeadsToday,
      pending_followups: pendingFollowups,
      overdue_followups: overdueFollowups,
      total_policies: totalPolicies,
      active_policies: activePolicies,
      total_quotations: totalQuotations,
      total_calls: totalCalls,
      active_claims: activeClaims,
      pending_rto: pendingRto,
      pending_fitness: pendingFitness,
      active_loans: activeLoans,
      total_customers: totalCustomers,
      total_employees: 0, // Will be users count
      today_visits: todayVisits,
    })
  } catch (error) {
    console.error('Dashboard Stats Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
