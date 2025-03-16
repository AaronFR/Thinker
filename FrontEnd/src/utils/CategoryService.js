import { apiFetch } from './authUtils';
import { toTitleCase } from './textUtils';
import { categoriesEndpoint } from '../constants/endpoints';

/**
 * Fetches categories from the backend, normalizes them for use.
 *
 * @returns {Promise<Array>} An array of formatted category objects.
 */
export const fetchCategories = async () => {
  try {
    const response = await apiFetch(categoriesEndpoint, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }

    const data = await response.json();

    // Process and normalize categories assuming data.categories is returned.
    return data.categories.map((category, index) => ({
      id: index + 1, // unique, sequential id
      name: toTitleCase(category.name),
      colour: category.colour || null,
      description: category.description || null,
    }));
  } catch (error) {
    console.error('Error in fetchCategories:', error);
    throw error;
  }
};
