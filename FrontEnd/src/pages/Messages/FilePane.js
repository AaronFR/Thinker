import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import FileItem from './FileItem';
import { withLoadingOpacity, toTitleCase } from '../../utils/textUtils';
import { apiFetch } from '../../utils/authUtils';

const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";

/**
 * FilePane Component
 * 
 * Displays a list of file categories and their respective files.
 * Allows users to expand/collapse categories, view file details, select files, and delete files.
 * 
 * @param onFileSelect: Callback function to handle file selection.
 * @param isProcessing: Indicates if the app is currently processing data.
 */
const FilePane = ({ onFileSelect, isProcessing, selectedFiles }) => {
  const [categories, setCategories] = useState([]);
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);
  const [fetchError, setFetchError] = useState('');
  const [loadingFiles, setLoadingFiles] = useState({}); // Track loading for each category

  const fetchCategories = useCallback(async () => {
    try {
      setFetchError('')

      const response = await apiFetch(`${FLASK_PORT}/categories_with_files`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error("Failed to get file categories");
      }

      const data = await response.json();

      const categoriesWithId = data.categories.map((category, index) => ({
        id: index + 1, // Assign a unique ID based on the index
        name: toTitleCase(category.name),
        colour: category.colour ? category.colour : null,
        files: []
      }));

      setCategories(categoriesWithId);
    } catch (error) {
      console.error("Error fetching file categories:", error);
      setFetchError('Unable to load file categories. Please try again later.');
    }
  }, []);

  const fetchFilesByCategory = useCallback(async (categoryName, categoryId) => {
    setLoadingFiles(prev => ({ ...prev, [categoryId]: true })); // Start loading for category
    
    try {
      const response = await apiFetch(`${FLASK_PORT}/files/${categoryName.toLowerCase()}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`Failed to get files for category: ${categoryName}`);
      }

      const data = await response.json();      
      setCategories(prevCategories =>
        prevCategories.map(category =>
          category.id === categoryId
            ? { ...category, files: data.files }
            : category
        )
      );
    } catch (error) {
      console.error("Error fetching files:", error);
      setFetchError(`Unable to load files for ${categoryName}. Please try again later.`);
    } finally {
      setLoadingFiles(prev => ({ ...prev, [categoryId]: false })); // End loading for category
    }
  }, []);
  /**
   * Toggles the expansion of a category.
   * If the category is already expanded, it collapses it.
   * Otherwise, it expands the category and fetches its files if not already loaded.
   * 
   * @param {number} id - The ID of the category.
   * @param {string} name - The name of the category.
   */
  const toggleCategory = useCallback(async (id, name) => {
    if (expandedCategoryId === id) {
      setExpandedCategoryId(null);
    } else {
      setExpandedCategoryId(id);
      const category = categories.find(cat => cat.id === id);
      if (!category?.files?.length) {
          await fetchFilesByCategory(name, id);
      }
    }
  }, [expandedCategoryId]);

  /**
   * Handles the deletion of a file by updating the state.
   * 
   * @param {number} categoryId: The ID of the category containing the file.
   * @param {number} fileId: The ID of the file to delete.
   */
  const handleDeleteFile = useCallback((categoryId, fileId) => {
    setCategories(prevCategories =>
      prevCategories.map(category =>
        category.id === categoryId 
          ? { ...category, files: category.files.filter(file => file.id !== fileId) } 
          : category
      )
    );
  }, []);

  /**
   * Fetches categories when the component mounts or when processing state changes.
   */
  useEffect(() => {
    if (!isProcessing) {
      fetchCategories();
    }
  }, [isProcessing]);

  return (
    <div className="files-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Files</h2>
      {fetchError && <p className="error-message" role="alert">{fetchError}</p>}
      <section className="category-list">
        {categories.length > 0 ? (
          categories.map((category) => (
            <div key={category.id} className="category-item" style={{ backgroundColor: category.colour}}>
              <header
                className="button category-title"
                onClick={() => toggleCategory(category.id, category.name)}
                role="button"
                aria-expanded={expandedCategoryId === category.id}
                aria-controls={`category-${category.id}`}
                tabIndex={0}
                onKeyPress={(e) => {
                      if (e.key === 'Enter') toggleCategory(category.id, category.name);
                }}
              >
                {category.name}
              </header>
              {expandedCategoryId === category.id && (
                <div id={`category-${category.id}`} className="file-list">
                  {loadingFiles[category.id] ? (
                    <p>Loading files...</p>
                  ) : (
                    category.files.length > 0 ? (
                      category.files.map((file) => (
                        <FileItem
                          key={file.id}
                          file={file}
                          onDelete={() => handleDeleteFile(category.id, file.id)}
                          onSelect={onFileSelect}
                          isSelected={selectedFiles?.some(selectedFile => selectedFile.id === file.id)}
                        />
                      ))
                    ) : (
                      <p>No files available in this category.</p>
                    )
                  )}
                </div>
              )}
            </div>
          ))
        ) : <div>Loading file categories...</div>}
      </section>
    </div>
  );
};

FilePane.propTypes = {
  onFileSelect: PropTypes.func.isRequired,
  isProcessing: PropTypes.bool.isRequired,
};

export default React.memo(FilePane);
