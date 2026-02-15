import { useState, useEffect } from 'react';

/**
 * A hook that types out text character by character.
 * @param text The full text to display
 * @param speed Speed in ms per character (default 20ms)
 * @param enabled Whether to enable the typing effect
 * @returns The current text to display and whether typing is complete
 */
export const useTypewriter = (text: string, speed: number = 20, enabled: boolean = true) => {
    const [displayText, setDisplayText] = useState('');
    const [isComplete, setIsComplete] = useState(false);

    useEffect(() => {
        if (!enabled) {
            setDisplayText(text);
            setIsComplete(true);
            return;
        }

        // Reset if text changes significantly (new message)
        setDisplayText('');
        setIsComplete(false);

        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                setDisplayText((prev) => prev + text.charAt(i));
                i++;
            } else {
                clearInterval(timer);
                setIsComplete(true);
            }
        }, speed);

        return () => clearInterval(timer);
    }, [text, speed, enabled]);

    // If text update is incremental (streaming), this logic needs adjustment.
    // But for "full text provided at once", this works.

    return { displayText, isComplete };
};
