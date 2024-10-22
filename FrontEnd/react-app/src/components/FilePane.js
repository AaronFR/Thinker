import React, { useState, useEffect } from 'react';
import './styles/FilePane.css'; // Ensure you create corresponding CSS
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const flask_port = "http://localhost:5000";

const FilePane = ({ onFileSelect, isProcessing }) => {
  const [categories, setCategories] = useState(null);
  const [expandedCategory, setExpandedCategory] = useState(null);

  const abridged_text_length = 160;

  const toggleCategory = async (id, name) => {
    console.log("HELLOOOOOOO")
    if (expandedCategory === id) {
      setExpandedCategory(null); // Collapse if already expanded
    } else {
      console.log("HElooooooo")
      setExpandedCategory(id); // Expand the clicked category

      // Check if this category already has files loaded
      const categoryIndex = categories.findIndex(cat => cat.id === id);
      if (categories[categoryIndex].files && categories[categoryIndex].files.length > 0) {
        // Files already loaded, no need to fetch again
        return;
      }

      await fetchFilesByCategory(name, id);
    }
  };

  function toTitleCase(string) {
    return string
      .toLowerCase()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${flask_port}/categories`, { // Assuming an endpoint for file categories
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

  const fetchFilesByCategory = async (categoryName, categoryId) => {
    try {
      const response = await fetch(`${flask_port}/categories/${categoryName.toLowerCase()}/files`, {
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

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleDeleteFile = (categoryId, fileId) => {
    const updatedCategories = categories.map((category) => {
      if (category.id === categoryId) {
        // Filter out the deleted file
        const updatedFiles = category.files.filter((file) => file.id !== fileId);
        return { ...category, files: updatedFiles };
      }
      return category;
    });

    setCategories(updatedCategories);
  };

  const FileItem = ({ file, onDelete }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    const toggleExpansion = () => {
      setIsExpanded(!isExpanded);
    };

    const shortenText = (text) => {
      return text.length > abridged_text_length ? text.slice(0, abridged_text_length) + '...' : text;
    };

    const shortenAndMarkupText = (text) => {
      const shortenedText = text.length > abridged_text_length ? text.slice(0, abridged_text_length) + '...' : text;
      const markedShortened = marked(shortenedText);
      return DOMPurify.sanitize(markedShortened);
    };

    const markedFull = (text) => {
      return DOMPurify.sanitize(marked(text));
    };

    const handleDelete = async (e) => {
      e.stopPropagation(); // Prevent triggering the toggleExpansion
      try {
        const response = await fetch(`${flask_port}/files/${file.id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          throw new Error("Failed to delete the file.");
        }

        onDelete(file.id);  // Call the onDelete callback to remove the file from the UI
      } catch (error) {
        console.error("Error deleting the file:", error);
      }
    };

    const handleSelect = () => {
      onFileSelect(file);
    };

    return (
      <div className="file-item" onClick={handleSelect} style={{ cursor: 'pointer' }}>
        <div onClick={toggleExpansion} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <p><strong>File Name:</strong> {isExpanded ? file.name : shortenText(file.name)}</p>
          <button onClick={handleDelete} className="delete-button">
            Delete
          </button>
        </div>
        {isExpanded && (
          <div className="file-details">
            <p><strong>Description:</strong> 
              <span 
                dangerouslySetInnerHTML={{ __html: markedFull(file.summary) }}
              />
            </p>
            <p className='time'>{new Date(file.time * 1000).toLocaleString()}</p>
            {/* Add more file details if necessary */}
          </div>
        )}
      </div>
    )};

  return (
    <div className="files-container" style={{ opacity: isProcessing ? 0.5 : 1 }}>
      <div className="sidebar">
        <h2>Files</h2>
        <div className="category-list">
          {categories && categories.length > 0 ? (
            categories.map(
              (category) => (
                <div key={category.id} className="category-item">
                  <div className="category-title" onClick={() => toggleCategory(category.id, category.name)}>
                    {category.name}
                  </div>
                  {expandedCategory === category.id && (
                    <div className="file-list">
                      {!category.files || category.files.length === 0 ? (
                        <p>Loading files...</p>
                      ) : (
                        category.files.map((file) => (
                          <FileItem
                            key={file.id}
                            file={file}
                            onDelete={() => handleDeleteFile(category.id, file.id)}
                          />
                        ))
                      )}
                    </div>
                  )}
                </div>
              )
            )
          ) : <div>Loading file categories...</div>}
        </div>
      </div>
    </div>
  );
};

export default FilePane;
