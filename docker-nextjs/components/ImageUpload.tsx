'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function ImageUpload({ onUploadSuccess }: { onUploadSuccess: (id: string) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [imageId, setImageId] = useState<string>('')

  const handleUpload = async () => {
    if (!file || !imageId) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`http://localhost:85/photo/${imageId}`, {
        method: 'PUT',
        body: formData,
      })

      if (response.ok) {
        alert('Image uploaded successfully')
        onUploadSuccess(imageId)
      } else {
        alert('Failed to upload image')
      }
    } catch (error) {
      console.error('Error uploading image:', error)
      alert('Error uploading image')
    }
  }

  return (
    <div className="space-y-2">
      <Input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <Input
        placeholder="Image ID"
        value={imageId}
        onChange={(e) => setImageId(e.target.value)}
      />
      <Button onClick={handleUpload}>Upload Image</Button>
    </div>
  )
}

