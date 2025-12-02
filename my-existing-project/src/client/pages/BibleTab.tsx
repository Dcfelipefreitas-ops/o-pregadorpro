import React from 'react';
import BibleViewer from '../components/BibleViewer';
import './bible.css';

const BibleTab: React.FC = () => {
    return (
        <div className="bible-tab">
            <h1>Bíblia em Português</h1>
            <BibleViewer />
        </div>
    );
};

export default BibleTab;