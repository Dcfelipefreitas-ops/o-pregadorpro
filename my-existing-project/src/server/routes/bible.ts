import { Router } from 'express';
import axios from 'axios';

const router = Router();

const BIBLE_API_URL = 'https://api.biblia.com/v1/bible/content/';

router.get('/portuguese', async (req, res) => {
    try {
        const response = await axios.get(`${BIBLE_API_URL}BIBLIA?passage=João 3:16&version=ARC`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ message: 'Error fetching Bible text', error: error.message });
    }
});

export default router;