'use client'

import { z } from "zod"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Form,
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormDescription,
    FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import axios from 'axios'
import { API } from '@/lib/conf'
import { useState } from "react"
import Link from "next/link"

const postSchema = z.object({
    event_title: z.string().min(1),
    date: z.string(),
    description: z.string(),
    good: z.string(),
    bad: z.string(),
    goal: z.string(),
    instructions: z.string(),
    posttype: z.enum(['ILP', 'messe', 'regular']),
})

export default function NewPost() {
    const [open, setOpen] = useState<boolean>(false)
    const today = new Date().toISOString().split('T')[0]

    const form = useForm<z.infer<typeof postSchema>>({
        resolver: zodResolver(postSchema),
        defaultValues: {
            event_title: '',
            date: today,
            description: '',
            good: '',
            bad: '',
            goal: '',
            instructions: '',
            posttype: 'regular',
        },
    })

    async function onSubmit(values: z.infer<typeof postSchema>) {
        try {
            await axios.post(`${API}/posts`, values)
            form.reset()
            setOpen(true)
        } catch (err) {
            console.error(err)
            alert('Failed')
        }
    }

    return <main className="px-20 py-12">
        <section>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8 max-w-xl p-4 mx-auto">
                    <FormField
                        control={form.control}
                        name="event_title"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Event Title</FormLabel>
                                <FormControl>
                                    <Input placeholder="München bauma 2025" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="date"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Date</FormLabel>
                                <FormControl>
                                    <Input type="date" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <FormField
                        control={form.control}
                        name="posttype"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>Type</FormLabel>
                                <Select onValueChange={field.onChange} defaultValue={field.value}>
                                    <FormControl>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select post type" />
                                        </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                        <SelectItem value="ILP">ILP</SelectItem>
                                        <SelectItem value="messe">Messe</SelectItem>
                                        <SelectItem value="regular">Regular</SelectItem>
                                    </SelectContent>
                                </Select>
                                <FormMessage />
                            </FormItem>
                        )}
                    />

                    {['description', 'good', 'bad', 'goal', 'instructions'].map((name) => (
                        <FormField
                            key={name}
                            control={form.control}
                            name={name as keyof z.infer<typeof postSchema>}
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>{name.charAt(0).toUpperCase() + name.slice(1)}</FormLabel>
                                    <FormControl>
                                        <Textarea {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                    ))}
                    <Button type="submit" className="w-full">Submit</Button>
                </form>
            </Form>
        </section>

        <section>
            <Dialog open={open} onOpenChange={setOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Post Created</DialogTitle>
                    </DialogHeader>
                    <p>Your post has been saved successfully. Draft will take some time to be created. You can leave the page and check the progress in content calander.</p>
                    <DialogFooter>
                        <Link href="/content-calander">Go to Content Calander</Link>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </section>
    </main>
}