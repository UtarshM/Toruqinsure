import { NextRequest, NextResponse } from 'next/server'
import prisma from '@/lib/prisma'
import { supabaseAdmin } from '@/lib/supabase-admin'

const BUCKET_NAME = 'documents'

export async function GET(req: NextRequest, { params }: { params: Promise<{ documentId: string }> }) {
  try {
    const { documentId } = await params
    const { searchParams } = new URL(req.url)
    const expiresIn = parseInt(searchParams.get('expiresIn') || '3600')

    const document = await prisma.document.findUnique({
      where: { id: documentId }
    })

    if (!document) {
      return NextResponse.json({ error: 'Document not found' }, { status: 404 })
    }

    // Generate signed URL
    const { data, error: urlError } = await supabaseAdmin.storage
      .from(BUCKET_NAME)
      .createSignedUrl(document.filePath, expiresIn)

    if (urlError || !data?.signedUrl) {
      return NextResponse.json({ error: `Could not generate signed URL: ${urlError?.message}` }, { status: 500 })
    }

    return NextResponse.json({
      documentId,
      fileName: document.fileName,
      signedUrl: data.signedUrl,
      expiresInSeconds: expiresIn
    })
  } catch (error: any) {
    console.error('Storage Signed URL GET Error:', error)
    return NextResponse.json({ error: error.message || 'Internal Server Error' }, { status: 500 })
  }
}
