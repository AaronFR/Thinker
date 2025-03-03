import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

import FileItem from './FileItem';
import { withLoadingOpacity, toTitleCase } from '../../utils/textUtils';
import { apiFetch } from '../../utils/authUtils';
import { categoriesWithFilesEndpoint, filesForCategoryNameEndpoint } from '../../constants/endpoints';

/**
 * FilePane Component
 * 
 * Displays a list of file categories and their respective files.
 * Allows users to expand/collapse categories, view file details, select files, and delete files.
 * 
 * @param onFileSelect - Callback function to handle file selection.
 * @param isProcessing - Indicates if the app is currently processing data.
 * @param selectedFiles - Currently selected files
 * @param refreshFiles - trigger for a refresh of the files
 */
const FilePane = ({ onFileSelect, isProcessing, selectedFiles, refreshFiles }) => {
  const [categories, setCategories] = useState([]);
  // Store file arrays separately keyed by category id.
  const [filesByCategory, setFilesByCategory] = useState({});
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);
  const [fetchError, setFetchError] = useState('');
  const [loadingFiles, setLoadingFiles] = useState({}); // Track loading status per category

  // Fetch categories (without embedding files) on mount or when not processing.
  const fetchCategories = useCallback(async () => {
    try {
      setFetchError('');
      const response = await apiFetch(categoriesWithFilesEndpoint, {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error("Failed to get file categories");
      }
      const data = await response.json();
      const cleanCategories = data.categories.map((category, index) => ({
        id: index + 1, // Unique ID based on index
        name: toTitleCase(category.name),
        colour: category.colour || null
      }));
      setCategories(cleanCategories);
    } catch (error) {
      console.error("Error fetching file categories:", error);
      setFetchError('Unable to load file categories. Please try again later.');
    }
  }, []);

  // Fetch files for a given category – store in filesByCategory state.
  const fetchFilesByCategory = useCallback(async (categoryName, categoryId) => {
    setLoadingFiles(prev => ({ ...prev, [categoryId]: true }));
    try {
      const response = await apiFetch(filesForCategoryNameEndpoint(categoryName.toLowerCase()), {
        method: "GET",
      });
      if (!response.ok) {
        throw new Error(`Failed to get files for category: ${categoryName}`);
      }
      const data = await response.json();
      setFilesByCategory(prev => ({ ...prev, [categoryId]: data.files }));
    } catch (error) {
      console.error("Error fetching files:", error);
      setFetchError(`Unable to load files for ${categoryName}. Please try again later.`);
    } finally {
      setLoadingFiles(prev => ({ ...prev, [categoryId]: false }));
    }
  }, []);

  /**
   * Toggles the expansion of a category. 
   * If the category is not expanded, it expands it and fetches its files if not already present.
   */
  const toggleCategory = useCallback(async (id, name) => {
    if (expandedCategoryId === id) {
      setExpandedCategoryId(null);
    } else {
      setExpandedCategoryId(id);
      // Only fetch if files are not already loaded.
      if (!filesByCategory[id]) {
        await fetchFilesByCategory(name, id);
      }
    }
  }, [expandedCategoryId, filesByCategory, fetchFilesByCategory]);

  /**
   * Handles deletion of a file by updating filesByCategory state.
   */
  const handleDeleteFile = useCallback((categoryId, fileId) => {
    setFilesByCategory(prev => ({
      ...prev,
      [categoryId]: prev[categoryId]?.filter(file => file.id !== fileId)
    }));
  }, []);

  // Fetch categories when component mounts and when processing completes.
  useEffect(() => {
    if (!isProcessing) {
      fetchCategories();
    }
  }, [isProcessing, refreshFiles, fetchCategories]);

  return (
    <div className="files-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Files</h2>
      {fetchError && <p className="error-message" role="alert">{fetchError}</p>}
      <section className="category-list">
        {categories.length > 0 ? (
          categories.map((category) => (
            <div key={category.id} className="category-item" style={{ backgroundColor: category.colour }}>
              <header
                className="button category-title"
                onClick={() => toggleCategory(category.id, category.name)}
                role="button"
                aria-expanded={expandedCategoryId === category.id}
                aria-controls={`category-${category.id}`}
                tabIndex={0}
                onKeyPress={(e) => { if (e.key === 'Enter') toggleCategory(category.id, category.name); }}
              >
                {category.name}
              </header>
              {expandedCategoryId === category.id && (
                <div id={`category-${category.id}`} className="message-list">
                  {loadingFiles[category.id] ? (
                    <p>Loading files...</p>
                  ) : (
                    filesByCategory[category.id] && filesByCategory[category.id].length > 0 ? (
                      filesByCategory[category.id].map((file) => (
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
        ) : (
          <div>Loading file categories...</div>
        )}
      </section>
    </div>
  );
};

FilePane.propTypes = {
  onFileSelect: PropTypes.func.isRequired,
  isProcessing: PropTypes.bool.isRequired,
  selectedFiles: PropTypes.array
};

export default React.memo(FilePane);
