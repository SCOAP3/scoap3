import { renderComplexSytnax } from '@/utils/utils';
import { useState } from 'react';
import { Text } from "react-mathjax2";

interface TitleWithSupportProps {
    title: string;
    showExtra: boolean;
}

export default function TitleWithSupport({ title, showExtra = false }: TitleWithSupportProps) {
    const [expanded, setExpanded] = useState(false);

    // Split at last '*'
    const lastAsteriskIndex = title.lastIndexOf('*');

    const mainTitle =
        lastAsteriskIndex !== -1 ? title.slice(0, lastAsteriskIndex).trim() : title.trim();

    const supportTextRaw =
        lastAsteriskIndex !== -1 ? title.slice(lastAsteriskIndex + 1).trim() : '';

    const hasSupportInfo = /support(ed)?/i.test(supportTextRaw);

    const toggle = () => setExpanded(!expanded);

    return (
        <div>
            <Text
                text={
                    <span
                        dangerouslySetInnerHTML={{
                            __html: renderComplexSytnax(mainTitle),
                        }}
                    />
                }
            />
            {showExtra && hasSupportInfo && (
                <span>
                    {!expanded ? (
                        <button
                            onClick={toggle}
                            style={{
                                color: 'blue',
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                margin: '0',
                                padding: '0',
                            }}
                        >
                            Show more
                        </button>
                    ) : (
                        <>
                            {' '}
                            — {supportTextRaw}{' '}
                            <button
                                onClick={toggle}
                                style={{
                                    color: 'blue',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    margin: '0',
                                    padding: '0',
                                }}
                            >
                                Show less
                            </button>
                        </>
                    )}
                </span>
            )}
        </div>
    );
}
