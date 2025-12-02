import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import BibleTab from './pages/BibleTab';

const App: React.FC = () => {
    return (
        <Router>
            <Switch>
                <Route path="/bible" component={BibleTab} />
                {/* Add other routes here as needed */}
            </Switch>
        </Router>
    );
};

export default App;