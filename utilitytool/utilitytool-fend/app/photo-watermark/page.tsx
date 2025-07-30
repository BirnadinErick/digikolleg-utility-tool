'use client'

import { useState } from 'react'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

import { Button } from "@/components/ui/button"
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from "@/components/ui/carousel"

async function downloadAsZip(images: string[]) {
    const zip = new JSZip()

    images.forEach((dataUrl, i) => {
        const base64 = dataUrl.split(',')[1]
        zip.file(`image-${i + 1}.jpg`, base64, { base64: true })
    })

    const content = await zip.generateAsync({ type: 'blob' })
    saveAs(content, 'watermarked-images.zip')
}

export default function PhotoWatermark() {
    const [images, setImages] = useState<File[]>([])
    const [watermarkedURLs, setWatermarkedURLs] = useState<string[]>([])
    const [previewUrls, setPreviewUrls] = useState<string[]>([])
    const [showPreview, setShowPreview] = useState<boolean>(true)

    const handleFiles = (files: FileList) => {
        const arr = Array.from(files)
        setImages(arr)
        Promise.all(arr.map(fileToDataURL)).then(setPreviewUrls)
    }

    const fileToDataURL = (file: File): Promise<string> => {
        return new Promise((res) => {
            const reader = new FileReader()
            reader.onloadend = () => res(reader.result as string)
            reader.readAsDataURL(file)
        })
    }

    async function parseImage(file: File, centerText: string, rightText = "Inecosys GmbH"): Promise<string> {
        const img = new Image()
        const dataURL = await fileToDataURL(file)
        img.src = dataURL

        return new Promise((resolve) => {
            img.onload = () => {
                const w = img.width
                const h = img.height
                const targetRatio = 16 / 9
                let newW = w
                let newH = Math.floor(w / targetRatio)

                if (newH > h) {
                    newH = h
                    newW = Math.floor(h * targetRatio)
                }

                const left = Math.floor((w - newW) / 2)
                const top = Math.floor((h - newH) / 2)

                const canvas = document.createElement('canvas')
                canvas.width = newW
                canvas.height = newH
                const ctx = canvas.getContext('2d')!

                ctx.drawImage(img, left, top, newW, newH, 0, 0, newW, newH)

                const fontSize = 36
                const paddingX = 16
                const paddingY = 16
                const textAreaHeight = fontSize + 2 * paddingY
                ctx.fillStyle = 'white'
                ctx.fillRect(0, newH - textAreaHeight, newW, textAreaHeight)

                ctx.fillStyle = 'black'
                ctx.font = `${fontSize}px sans-serif`
                ctx.textBaseline = 'top'

                const leftX = 20
                ctx.fillText(centerText, leftX, newH - textAreaHeight + paddingY)

                const rightTextWidth = ctx.measureText(rightText).width
                const rightX = newW - rightTextWidth - paddingX
                ctx.fillText(rightText, rightX, newH - textAreaHeight + paddingY)

                resolve(canvas.toDataURL('image/jpeg'))
            }
        })
    }

    const addWatermark = async () => {
        const urls = await Promise.all(
            images.map(file => parseImage(file, "DigiKolleg 2025 Final Presentation")))

        setWatermarkedURLs(urls)
    }

    return <main className="p-20 space-y-12">
        <section className='space-y-3'>
            <p className="text-lg font-bold">1. Upload the photos</p>
            <input className='bg-neutral-50 p-2' type="file" accept="image/*" multiple onChange={(e) => handleFiles(e.target.files!)} />

            {
                previewUrls.length > 0 && showPreview &&
                <Carousel className="w-full max-w-2/5">
                    <CarouselContent>
                        {previewUrls.map((url, index) => (
                            <CarouselItem key={index}>
                                <div key={index} className="flex-[0_0_100%] p-2">
                                    <img src={url} className="w-full max-w-[480px] h-auto object-contain rounded-xl" />
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious />
                    <CarouselNext />
                </Carousel>
            }

        </section>

        <section className="space-y-3">
            <p className="text-lg font-bold">2. Run command</p>
            <p className='text-neutral-500'>Clicking on Run will send the photos to cloud and process it. By clicking you are consenting to this.</p>
            <Button variant="default" onClick={() => {
                setShowPreview(false);
                addWatermark();
            }}>Add Watermark</Button>
        </section>

        <section className="space-y-3">
            <p className="text-lg font-bold">3. Download the photos</p>
            <p className='text-neutral-500'>When your files have been processed, download it as zip file.</p>
            {watermarkedURLs.length > 0 && (
                <Button onClick={() => downloadAsZip(watermarkedURLs)}>
                    Download as .zip file
                </Button>
            )}

            {
                watermarkedURLs.length > 0 &&
                <Carousel className="w-full max-w-2/5">
                    <CarouselContent>
                        {watermarkedURLs.map((url, index) => (
                            <CarouselItem key={index}>
                                <div key={index} className="flex-[0_0_100%] p-2">
                                    <img src={url} className="w-full max-w-[480px] h-auto object-contain rounded-xl" />
                                </div>
                            </CarouselItem>
                        ))}
                    </CarouselContent>
                    <CarouselPrevious />
                    <CarouselNext />
                </Carousel>
            }
        </section>
    </main>
}