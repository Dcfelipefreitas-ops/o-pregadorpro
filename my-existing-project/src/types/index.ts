export interface BibleVerse {
    id: number;
    text: string;
    chapter: number;
    verse: number;
}

export interface BibleBook {
    id: number;
    name: string;
    chapters: number;
}

export interface BibleTranslation {
    id: number;
    name: string;
    language: string;
}

export interface BibleResponse {
    book: BibleBook;
    verses: BibleVerse[];
}

export type Language = 'pt' | 'en' | 'es'; // Add more languages as needed

export interface FetchBibleParams {
    bookId: number;
    chapter: number;
    translation: Language;
}