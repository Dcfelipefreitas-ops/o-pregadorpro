import React, { useEffect, useState } from 'react';
import { fetchBibleText } from '../services/bibleApi';
import { useBible } from '../hooks/useBible';
import './bible.css';

const BibleViewer: React.FC = () => {
    const { bibleText, loading, error } = useBible();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error loading Bible text: {error.message}</div>;
    }

    return (
        <div className="bible-viewer">
            <h2>Bíblia em Português</h2>
            <div className="bible-text" dangerouslySetInnerHTML={{ __html: bibleText }} />
        </div>
    );
};

export default BibleViewer;