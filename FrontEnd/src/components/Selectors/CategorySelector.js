import React, { useState, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import TagSelector from './TagsSelector';
import TooltipConstants from '../../constants/tooltips';
import { fetchCategories } from '../../utils/CategoryService';

/** 
 * Displays the automatically selected category and lets the user select their own
 * 
 * @param {string} selectedCategory- Current selected category.
 * @param {function} setTags - Function to update the selected tags.
 */
const CategorySelector = React.memo(({ selectedCategory, setTags }) => {
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const loadCategories = useCallback(async () => {
    setIsLoading(true);
    try {
      setError('');
      const cats = await fetchCategories();
      // Format categories for TagSelector (assuming it needs value/label)
      const formattedCategories = cats.map(cat => ({
        value: cat.name.toLowerCase(),
        label: cat.name,
      }));
      setCategories(formattedCategories);
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

  useEffect(() => {
    const addMissingCategory = async () => {
      const formattedCategories = await loadCategories();
      const categoryExists = formattedCategories?.some(
        (cat) => cat.value === selectedCategory
      );

      if (selectedCategory && !categoryExists) {
        const newCategory = {
          value: selectedCategory.toLowerCase(),
          label: `*NEW* - ${selectedCategory}`,
        };
        setCategories((prevCategories) => [...prevCategories, newCategory]);
      }
    };

    addMissingCategory();
  }, [loadCategories, selectedCategory]);

  return (
    <div
      className='category-selector-container'
      data-tooltip-id="tooltip"
      data-tooltip-content={TooltipConstants.categorySelector}
      data-tooltip-place="top"
    >
      <TagSelector
        selectedValue={selectedCategory}
        setTags={setTags}
        options={categories}
        placeholder="Category"
        className="category-selector"
      />
    </div>
    
  );
});

CategorySelector.propTypes = {
  selectedCategory: PropTypes.string.isRequired,
  setTags: PropTypes.func.isRequired,
};

export default CategorySelector;
