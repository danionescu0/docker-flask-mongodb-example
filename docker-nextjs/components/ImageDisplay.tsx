'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'

export default function ImageDisplay({ imageId, resizeHeight }: { imageId: string; resizeHeight: string }) {
  const [imageUrl, setImageUrl] = useState<string | null>(null)

  useEffect(() => {
    if (imageId) {
      const url = `http://localhost:85/photo/${imageId}${resizeHeight ? `?resize=${resizeHeight}` : ''}`
      setImageUrl(url)
    } else {
      setImageUrl(null)
    }
  }, [imageId, resizeHeight])

  if (!imageUrl) return null

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold mb-2">Current Image</h2>
      <Image src={imageUrl} alt="Displayed Image" width={300} height={300} className="object-contain" />
    </div>
  )
}

