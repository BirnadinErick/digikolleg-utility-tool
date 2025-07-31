'use client'

import 'react-big-calendar/lib/css/react-big-calendar.css'
import { Calendar, Event as CalendarEvent, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import enUS from 'date-fns/locale/en-US'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { useState } from "react"
import { Button } from "@/components/ui/button"

interface PostEvent {
    title: string;
    date: string;
    type: string;
    tags: string;
    id: string | number;
}

const demoPosts: PostEvent[] = [
    {
        'title': 'Title101',
        'date': '2025-07-30',
        'type': 'ILP',
        'tags': '#hello #hi #yo',
        'id': '2004'
    },
    {
        'title': 'Title101',
        'date': '2025-07-31',
        'type': 'ILP',
        'tags': '#hello #hi #yo',
        'id': '2005'
    },
    {
        'title': 'Title101',
        'date': '2025-07-23',
        'type': 'ILP',
        'tags': '#hello #hi #yo',
        'id': '2006'
    },
    {
        'title': 'Title104',
        'date': '2025-07-30',
        'type': 'ILP',
        'tags': '#hello #hi #yo',
        'id': '2003'
    },
]

function TableView(postEvents: PostEvent[]) {
    return <section className="max-w-4/5 py-12">
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]">Title</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead className="">Tags</TableHead>
                    <TableHead></TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {postEvents.map((post) => (
                    <TableRow key={post.id}>
                        <TableCell className="min-w-[480px] font-medium">{post.title}</TableCell>
                        <TableCell className="">{post.date}</TableCell>
                        <TableCell>{post.type}</TableCell>
                        <TableCell>{post.tags}</TableCell>
                        <TableCell className="text-right">
                            <DropdownMenu>
                                <DropdownMenuTrigger>
                                    <Button variant="ghost">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                                            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                                        </svg>
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent>
                                    <DropdownMenuLabel>Calendar Actions</DropdownMenuLabel>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem>Post now</DropdownMenuItem>
                                    <DropdownMenuItem>Edit</DropdownMenuItem>
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem className="bg-red-500">Delete</DropdownMenuItem>
                                </DropdownMenuContent>
                            </DropdownMenu></TableCell>
                    </TableRow>
                ))}
            </TableBody>
        </Table>

    </section>
}

const localizer = dateFnsLocalizer({
    format,
    parse,
    startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
    getDay,
    locales: { 'en-US': enUS },
})

function CalendarView(postEvents: PostEvent[]) {
    const events: CalendarEvent[] = postEvents.map((post) => ({
        title: post.title,
        start: new Date(post.date),
        end: new Date(post.date),
        allDay: true,
    }))

    return <section className="py-3 h-[900px]">
        <Calendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            views={['month']}
            style={{ height: '100%' }}
        />
    </section>
}

export default function ContentCalander() {
    const [showCalendar, setShowCalendar] = useState<boolean>(false)
    return <main className="px-20 py-12">
        <section className="flex justify-start items-center space-x-4">
            <Switch checked={showCalendar} onCheckedChange={() => setShowCalendar(!showCalendar)} />
            <p>Calendar View</p>
        </section>

        {showCalendar ? CalendarView(demoPosts) : TableView(demoPosts)}
    </main>
}