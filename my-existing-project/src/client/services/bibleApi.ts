import axios from 'axios';

const BASE_URL = 'https://api.biblia.com/v1/bible'; // Replace with the actual Bible API URL
const API_KEY = 'YOUR_API_KEY'; // Replace with your actual API key

export const fetchBibleInPortuguese = async (version: string = 'NVI') => {
    try {
        const response = await axios.get(`${BASE_URL}/content/${version}.txt`, {
            params: {
                key: API_KEY,
                language: 'pt' // Portuguese
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching Bible text:', error);
        throw error;
    }
};