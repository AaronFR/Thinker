import React, { useState, useEffect } from 'react';

import FileItem from './FileItem';
import { withLoadingOpacity } from '../utils/textUtils';

const flask_port = "http://localhost:5000";

/**
 * FilePane Component
 * 
 * Displays a list of file categories and their respective files.
 * Allows users to expand/collapse categories, view file details, select files, and delete files.
 * 
 * Props:
 * - onFileSelect (function): Callback function to handle file selection.
 * - isProcessing (boolean): Indicates if the app is currently processing data.
 */
const FilePane = ({ onFileSelect, isProcessing }) => {
  const [categories, setCategories] = useState([]);
  const [expandedCategoryId, setExpandedCategoryId] = useState(null);

  // Fetch categories on mount and when finished processing
  useEffect(() => {
    if (!isProcessing) {
      // First fetch after 5 seconds
      const firstTimeout = setTimeout(() => {
        fetchCategories();
      }, 5000);
  
      // Second fetch after an additional 10 seconds (total of 15 seconds from prompt completion)
      const secondTimeout = setTimeout(() => {
        fetchCategories();
      }, 15000);
  
      // Clear timeouts if the component unmounts or promptCompleted changes
      return () => {
        clearTimeout(firstTimeout);
        clearTimeout(secondTimeout);
      };
    }
  }, [isProcessing]);

  function toTitleCase(string) {
    return string
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
 
  const fetchCategories = async () => {
    try {
      const response = await fetch(`${flask_port}/categories_with_files`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error("Failed to get file categories");
      }

      const data = await response.json();

      const categoriesWithId = data.categories.map((category, index) => ({
        id: index + 1, // Assign a unique ID based on the index
        name: toTitleCase(category),
        files: []
      }));

      setCategories(categoriesWithId);
    } catch (error) {
      console.error("Error fetching file categories:", error);
    }
  };

  /**
   * Toggles the expansion of a category.
   * If the category is already expanded, it collapses it.
   * Otherwise, it expands the category and fetches its files if not already loaded.
   * 
   * @param {number} id - The ID of the category.
   * @param {string} name - The name of the category.
   */
  const toggleCategory = async (id, name) => {
    if (expandedCategoryId === id) {
      setExpandedCategoryId(null);
      return
    }

    setExpandedCategoryId(id); // Expand the clicked category

    // Check if this category already has files loaded
    const category  = categories.find(cat => cat.id === id);
    if (category.files && category.files.length > 0) {
      // Files already loaded, no need to fetch again
      return;
    }

    await fetchFilesByCategory(name, id);
  };

  const fetchFilesByCategory = async (categoryName, categoryId) => {
    try {
      const response = await fetch(`${flask_port}/files/${categoryName.toLowerCase()}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get files for category: ${categoryName}`);
      }

      const data = await response.json();      

      setCategories(prevCategories =>
        prevCategories.map(category =>
          category.id === categoryId ? { ...category, files: data.files } : category
        )
      );
    } catch (error) {
      console.error("Error fetching files:", error);
    }
  };

  const handleDeleteFile = (categoryId, fileId) => {
    setCategories(prevCategories =>
      prevCategories.map(category => {
        if (category.id === categoryId) {
          const updatedFiles = category.files.filter(file => file.id !== fileId);
          return { ...category, files: updatedFiles };
        }
        return category;
      })
    );
  };

  return (
    <div className="files-container" style={withLoadingOpacity(isProcessing)}>
      <h2>Files</h2>
      <section className="category-list">
        {categories.length > 0 ? (
          categories.map((category) => (
            <div key={category.id} className="category-item">
              <div className="category-title" onClick={() => toggleCategory(category.id, category.name)}>
                {category.name}
              </div>
              {expandedCategoryId === category.id && (
                <div className="file-list">
                  {category.files.length === 0 ? (
                    <p>Loading files...</p>
                  ) : (
                    category.files.map((file) => (
                      <FileItem
                        key={file.id}
                        file={file}
                        onDelete={() => handleDeleteFile(category.id, file.id)}
                        onSelect={onFileSelect}
                      />
                    ))
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

export default FilePane;
