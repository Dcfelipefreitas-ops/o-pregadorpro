import express from 'express';
import bibleRoutes from './routes/bible';

const app = express();
const PORT = process.env.PORT || 5000;

app.use(express.json());
app.use('/api/bible', bibleRoutes);

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});