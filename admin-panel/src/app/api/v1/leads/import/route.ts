import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'

/**
 * POST /api/v1/leads/import
 * Expects an array of leads with assignment info.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { leads } = body // Array of { client_name, client_phone, assigned_to_email, ... }

    if (!Array.isArray(leads)) {
      return NextResponse.json({ error: 'Invalid data format' }, { status: 400 })
    }

    // 1. Fetch all users to map emails to IDs
    const users = await prisma.user.findMany({
      select: { id: true, email: true }
    })
    const userMap = new Map(users.map(u => [u.email, u.id]))

    // 2. Prepare data for bulk create
    const leadsToCreate = leads.map(l => ({
      clientName: l.client_name,
      clientPhone: String(l.client_phone),
      clientEmail: l.client_email || null,
      status: 'New',
      assignedTo: userMap.get(l.assigned_to_email) || null
    }))

    // 3. Perform bulk create
    const created = await prisma.lead.createMany({
      data: leadsToCreate,
      skipDuplicates: true
    })

    return NextResponse.json({ 
      success: true, 
      count: created.count,
      message: `Successfully imported ${created.count} leads.`
    })
  } catch (error) {
    console.error('Bulk Import Error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
