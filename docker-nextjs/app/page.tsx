'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import ImageUpload from '@/components/ImageUpload'
import ImageDisplay from '@/components/ImageDisplay'
import ImageSearch from '@/components/ImageSearch'

export default function Home() {
  const [currentImageId, setCurrentImageId] = useState<string>('')
  const [resizeHeight, setResizeHeight] = useState<string>('')

  const handleGetImage = async () => {
    if (!currentImageId) return
    const url = `http://localhost:85/photo/${currentImageId}${resizeHeight ? `?resize=${resizeHeight}` : ''}`
    window.open(url, '_blank')
  }

  const handleDeleteImage = async () => {
    if (!currentImageId) return
    try {
      const response = await fetch(`http://localhost:85/photo/${currentImageId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        alert('Image deleted successfully')
        setCurrentImageId('')
      } else {
        alert('Failed to delete image')
      }
    } catch (error) {
      console.error('Error deleting image:', error)
      alert('Error deleting image')
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Image Processing UI</h1>
      <Tabs defaultValue="upload" className="w-full">
        <TabsList>
          <TabsTrigger value="upload">Upload & Manage</TabsTrigger>
          <TabsTrigger value="search">Search Similar</TabsTrigger>
        </TabsList>
        <TabsContent value="upload">
          <Card>
            <CardHeader>
              <CardTitle>Upload & Manage Images</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <ImageUpload onUploadSuccess={(id) => setCurrentImageId(id)} />
                <div className="flex space-x-2">
                  <Input
                    placeholder="Image ID"
                    value={currentImageId}
                    onChange={(e) => setCurrentImageId(e.target.value)}
                  />
                  <Input
                    placeholder="Resize Height"
                    value={resizeHeight}
                    onChange={(e) => setResizeHeight(e.target.value)}
                  />
                  <Button onClick={handleGetImage}>Get Image</Button>
                  <Button onClick={handleDeleteImage} variant="destructive">Delete Image</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="search">
          <Card>
            <CardHeader>
              <CardTitle>Search Similar Images</CardTitle>
            </CardHeader>
            <CardContent>
              <ImageSearch />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      <ImageDisplay imageId={currentImageId} resizeHeight={resizeHeight} />
    </div>
  )
}

