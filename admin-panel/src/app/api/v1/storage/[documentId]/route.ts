import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { supabaseAdmin } from '@/lib/supabase-admin'

const BUCKET_NAME = 'documents'

export async function DELETE(req: NextRequest, { params }: { params: Promise<{ documentId: string }> }) {
  try {
    const { documentId } = await params

    const document = await prisma.document.findUnique({
      where: { id: documentId }
    })

    if (!document) {
      return NextResponse.json({ error: 'Document not found' }, { status: 404 })
    }

    // Remove from Supabase Storage
    const { error: removeError } = await supabaseAdmin.storage
      .from(BUCKET_NAME)
      .remove([document.filePath])

    if (removeError) {
      console.error('Failed to remove file from Supabase storage:', removeError)
      // We log but continue to delete the DB record to keep them in sync
    }

    // Delete DB record
    await prisma.document.delete({
      where: { id: documentId }
    })

    return NextResponse.json({ detail: 'Document deleted successfully', documentId })
  } catch (error: any) {
    console.error('Storage DELETE Error:', error)
    return NextResponse.json({ error: error.message || 'Internal Server Error' }, { status: 500 })
  }
}
