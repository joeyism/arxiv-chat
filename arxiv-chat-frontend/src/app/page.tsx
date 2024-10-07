'use client';
import Image from 'next/image';
import { AiChat , useAsStreamAdapter } from '@nlux/react';
import { streamText } from './stream';
import '@nlux/themes/nova.css';

export default function HomePage() {

    // We transform the streamText function into an adapter that <AiChat /> can use
    const chatAdapter = useAsStreamAdapter(streamText);

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24" style={{"height": "600px"}}>
            <div className="aiChat-container" style={{"height": "100%", "width": "100%"}}>
                <AiChat
                    adapter={chatAdapter}
                    personaOptions={{
                        assistant: {
                            name: 'PaperChat',
                            avatar: 'https://media.licdn.com/dms/image/v2/C4D0BAQFvfCbDvcFlIg/company-logo_200_200/company-logo_200_200/0/1676326613718?e=2147483647&v=beta&t=GZ4Nn1WF-UamFcA1P1hP8_IasdhHmOPflgiU68XYWwA',
                            tagline: 'Let me help you find papers and understand topics',
                        },
                        user: {
                            name: 'You',
                            avatar: 'https://avatars.githubusercontent.com/u/7503144?v=4',
                        },
                    }}
                    conversationOptions={{
                        conversationStarters: [
                            {prompt: 'What is an LLM'},
                            {prompt: 'What are some papers on synthetic population generation?'},
                            {prompt: 'What are some papers on LLM quantization?'},
                        ],
                    }}
                    displayOptions={{
                        width: "100%",
                        height: "100%",
                    }}
                />
            </div>
        </main>
    );
}

const PageHeader = () => {
    return (
        <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
            <p className="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-gradient-to-b from-zinc-200 pb-6 pt-8 backdrop-blur-2xl dark:border-neutral-800 dark:bg-zinc-800/30 dark:from-inherit lg:static lg:w-auto  lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4 lg:dark:bg-zinc-800/30">
                Get started at&nbsp;
                <a href="https://docs.nlkit.com/nlux" target="_blank"
                   className="font-mono font-bold">docs.nlkit.com/nlux</a>
            </p>
            <div
                className="fixed bottom-0 left-0 flex h-48 w-full items-end justify-center bg-gradient-to-t from-white via-white dark:from-black dark:via-black lg:static lg:size-auto lg:bg-none">
                <a
                    className="pointer-events-none flex place-items-center gap-2 p-8 lg:pointer-events-auto lg:p-0"
                    href="https://docs.nlkit.com/nlux"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    By{' '}
                    <Image
                        src="/nlux.svg"
                        alt="NLUX Logo"
                        className="dark:invert"
                        width={100}
                        height={32}
                        priority
                    />
                </a>
            </div>
        </div>
    );
};

const PageFooter = () => {
    return (
        <div className="mb-32 grid text-center lg:mb-0 lg:w-full lg:max-w-5xl lg:grid-cols-3 lg:text-left">
            <a
                href="https://docs.nlkit.com/nlux"
                className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                target="_blank"
                rel="noopener noreferrer"
            >
                <h2 className="mb-3 text-2xl font-semibold">
                    Docs{' '}
                    <span
                        className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
                </h2>
                <p className="m-0 max-w-[30ch] text-sm opacity-50">
                    Find in-depth information about NLUX features and API.
                </p>
            </a>

            <a
                href="https://docs.nlkit.com/nlux/learn/overview"
                className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                target="_blank"
                rel="noopener noreferrer"
            >
                <h2 className="mb-3 text-2xl font-semibold">
                    Learn{' '}
                    <span
                        className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
                </h2>
                <p className="m-0 max-w-[30ch] text-sm opacity-50">
                    Learn about NLUX through several guides and examples.
                </p>
            </a>

            <a
                href="https://docs.nlkit.com/nlux/examples"
                className="group rounded-lg border border-transparent px-5 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                target="_blank"
                rel="noopener noreferrer"
            >
                <h2 className="mb-3 text-2xl font-semibold">
                    Examples{' '}
                    <span
                        className="inline-block transition-transform group-hover:translate-x-1 motion-reduce:transform-none">
              -&gt;
            </span>
                </h2>
                <p className="m-0 max-w-[30ch] text-sm opacity-50">
                    Explore examples of AI assistants built with NLUX.
                </p>
            </a>
        </div>
    );
};
