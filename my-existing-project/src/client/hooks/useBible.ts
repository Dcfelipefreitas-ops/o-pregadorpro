import { useEffect, useState } from 'react';
import { fetchBibleText } from '../services/bibleApi';

const useBible = () => {
    const [bibleText, setBibleText] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getBibleText = async () => {
            try {
                setLoading(true);
                const text = await fetchBibleText();
                setBibleText(text);
            } catch (err) {
                setError('Failed to fetch Bible text');
            } finally {
                setLoading(false);
            }
        };

        getBibleText();
    }, []);

    return { bibleText, loading, error };
};

export default useBible;