import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { supabaseAdmin } from '@/lib/supabase-admin'
import { v4 as uuidv4 } from 'uuid'

const BUCKET_NAME = 'documents'

const ENTITY_FOLDERS: Record<string, string> = {
  lead: 'leads',
  policy: 'policies',
  quotation: 'quotations',
  kyc: 'kyc',
  claim: 'claims',
}

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData()
    const entityType = formData.get('entityType') as string
    const entityId = formData.get('entityId') as string
    const file = formData.get('file') as File | null
    const uploadedBy = formData.get('uploadedBy') as string | null

    if (!entityType || !entityId || !file) {
      return NextResponse.json({ error: 'entityType, entityId, and file are required' }, { status: 400 })
    }

    if (!ENTITY_FOLDERS[entityType]) {
      return NextResponse.json({ error: `Invalid entityType. Must be one of: ${Object.keys(ENTITY_FOLDERS).join(', ')}` }, { status: 400 })
    }

    // Prepare file path
    const folder = ENTITY_FOLDERS[entityType]
    const safeName = file.name.replace(/\s+/g, '_')
    const uniqueName = `${uuidv4()}_${safeName}`
    const storagePath = `${folder}/${entityId}/${uniqueName}`

    // Upload to Supabase Storage
    const buffer = Buffer.from(await file.arrayBuffer())
    const { error: uploadError } = await supabaseAdmin.storage
      .from(BUCKET_NAME)
      .upload(storagePath, buffer, {
        contentType: file.type || 'application/octet-stream',
        upsert: false
      })

    if (uploadError) {
      return NextResponse.json({ error: `Storage upload failed: ${uploadError.message}` }, { status: 500 })
    }

    // Save document record to DB
    const document = await prisma.document.create({
      data: {
        entityType,
        entityId,
        fileName: file.name || 'upload',
        filePath: storagePath,
        uploadedBy: uploadedBy || null,
      }
    })

    // Log Activity
    if (uploadedBy) {
      await prisma.activityLog.create({
        data: {
          userId: uploadedBy,
          action: 'uploaded_document',
          entityType,
          entityId,
          metadata: { fileName: file.name, documentId: document.id }
        }
      })
    }

    return NextResponse.json(document)
  } catch (error: any) {
    console.error('Storage Upload POST Error:', error)
    return NextResponse.json({ error: error.message || 'Internal Server Error' }, { status: 500 })
  }
}
