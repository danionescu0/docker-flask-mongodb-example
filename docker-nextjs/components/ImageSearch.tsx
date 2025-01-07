'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Slider } from '@/components/ui/slider'
import Image from 'next/image'
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ReloadIcon } from "@radix-ui/react-icons"
import { API_URL } from '../app/config'

export default function ImageSearch() {
  const [file, setFile] = useState<File | null>(null)
  const [similarImages, setSimilarImages] = useState<number[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [similarity, setSimilarity] = useState(20)
  const [resize, setResize] = useState(300)
  const [rotate, setRotate] = useState(0)
  const [brightness, setBrightness] = useState(1)

  const handleSearch = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setIsLoading(true)
    setError(null)
    setSimilarImages([])

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_URL}/photo/similar?similarity=${similarity}`, {
        method: 'PUT',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('API Response:', result)

      if (Array.isArray(result)) {
        setSimilarImages(result)
      } else {
        throw new Error('Unexpected response format: not an array')
      }
    } catch (error) {
      console.error('Error searching similar images:', error)
      setError(`Error searching similar images: ${error instanceof Error ? error.message : String(error)}`)
    } finally {
      setIsLoading(false)
    }
  }

  const getImageUrl = (id: number) => {
    return `${API_URL}/photo/${id}?resize=${resize}&rotate=${rotate}&brightness=${brightness}`
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Input 
          type="file" 
          onChange={(e) => {
            const selectedFile = e.target.files?.[0]
            if (selectedFile) {
              setFile(selectedFile)
              setError(null)
            }
          }} 
        />
        <div className="flex items-center space-x-2">
          <span>Similarity:</span>
          <Slider
            value={[similarity]}
            onValueChange={(value) => setSimilarity(value[0])}
            max={40}
            step={1}
          />
          <span>{similarity}</span>
        </div>
        <Button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? (
            <>
              <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
              Searching...
            </>
          ) : (
            'Search Similar Images'
          )}
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {similarImages.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Similar Images</h3>
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <span>Resize:</span>
              <Slider
                value={[resize]}
                onValueChange={(value) => setResize(value[0])}
                max={1000}
                step={10}
              />
              <span>{resize}px</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>Rotate:</span>
              <Slider
                value={[rotate]}
                onValueChange={(value) => setRotate(value[0])}
                max={360}
                step={45}
              />
              <span>{rotate}°</span>
            </div>
            <div className="flex items-center space-x-2">
              <span>Brightness:</span>
              <Slider
                value={[brightness]}
                onValueChange={(value) => setBrightness(value[0])}
                min={0.1}
                max={2}
                step={0.1}
              />
              <span>{brightness.toFixed(1)}</span>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4">
            {similarImages.map((imageId) => (
              <Image
                key={imageId}
                src={getImageUrl(imageId)}
                alt={`Similar Image ${imageId}`}
                width={resize}
                height={resize}
                className="object-cover"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

