import React, { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';
import { fetchCategories } from '../../utils/CategoryService';

/**
 * @typedef {object} Category
 * @property {string} value - The category value (lowercase name).
 * @property {string} label - The category label (display name).
 */

/**
 * Displays the automatically selected category and lets the user select their own
 *
 * @param {string} selectedCategory - Current selected category.
 * @param {function} setTags - Function to update the selected tags.
 */
const CategorySelector = React.memo(({ selectedCategory, setTags }) => {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Fetches categories from the server and formats them for the TagSelector.
   * 
   * ToDo: Category management needs to be centrally managed to avoid multiple calls and update sensibly
   */
  const loadCategories = useCallback(async () => {
    setIsLoading(true);
    try {
      setError('');
      const cats = await fetchCategories();
      /** @type {Category[]} */
      const formattedCategories = cats.map(cat => ({
        value: cat.name.toLowerCase(),
        label: cat.name,
      }));
      setCategories(formattedCategories);
      return formattedCategories; // Return formatted categories for use in addMissingCategory
    } catch (err) {
      setError('Unable to load categories. Please try again.');
      console.error(err); // Log the error for debugging
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  /**
   * Adds a missing category to the list if it's not already present.
   * 
   * Will update the list of categories if a new category is being added to *confirm*
   * the missingCategory hasn't been added since initiation
   */
  const addMissingCategory = useCallback(async () => {
    if (!selectedCategory) return;

    const formattedCategories = await loadCategories();

    // ToDo: bug for new users with no categories yet?
    if (!formattedCategories) return; // Exit if loading categories failed

    const categoryExists = formattedCategories.some(
      (cat) => cat.value === selectedCategory.toLowerCase()
    );

    if (!categoryExists) {
      /** @type {Category} */
      const newCategory = {
        value: selectedCategory.toLowerCase(),
        label: `*NEW* - ${selectedCategory}`,
      };
      setCategories((prevCategories) => {
        // Check if the category is already in prevCategories to avoid duplicates
        const alreadyExists = prevCategories.some(cat => cat.value === newCategory.value);
        if (alreadyExists) {
          return prevCategories;
        }
        return [...prevCategories, newCategory];
      });
    }
  }, [loadCategories, selectedCategory]);

  useEffect(() => {
    addMissingCategory();
  }, [addMissingCategory]);

  return (
    <div
      className='category-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.categorySelector}
      data-tooltip-place="top"
    >
      {error && (
        <div
          className="error-message"
          role="alert"
          aria-live="assertive" // Announce the error immediately
          style={{ color: 'red', marginBottom: '10px' }} // Basic styling, customize as needed
        >
          {error}
        </div>
      )}
      <TagSelector
        selectedValue={selectedCategory}
        setTags={setTags}
        options={categories}
        placeholder="Category"
        className="category-selector"
        creatable={true}
      />
    </div>
  );
});

CategorySelector.propTypes = {
  selectedCategory: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default CategorySelector;
