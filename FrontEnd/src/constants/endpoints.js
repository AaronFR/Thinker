

export const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";


/* Auth */

export const loginEndpoint = `${FLASK_PORT}/login`;
export const registerEndpoint = `${FLASK_PORT}/register`;
export const validateSessionEndpoint = `${FLASK_PORT}/auth/validate`;
export const refreshSessionEndpoint = `${FLASK_PORT}/refresh`;
export const logoutSessionEndpoint = `${FLASK_PORT}/logout`;

/* Augmentation */

export const autoEngineerPromptEndpoint = `${FLASK_PORT}/augmentation/augment_prompt`;
export const questionPromptEndpoint = `${FLASK_PORT}/augmentation/question_prompt`
export const selectPersonaEndpoint = `${FLASK_PORT}/augmentation/select_persona`;
export const selectWorkflowEndpoint = `${FLASK_PORT}/augmentation/select_workflow`;

/* Categories */

export const fetchCategoriesEndpoint = `${FLASK_PORT}/categories`

/* Files */

export const fileUploadEndpoint = `${FLASK_PORT}/file`;
export function readFileEndpoint(uuid) {
  return `${FLASK_PORT}/read_file/${uuid}`
}
export const readStagedFilesEndpoint = `${FLASK_PORT}/list_staged_files`
export function deleteFileEndpoint(fileId) {
  return `${FLASK_PORT}/file/${fileId}`
}

export function fetchFilesForCategoryEndpoint(categoryId, fileName) {
  return `${FLASK_PORT}/file/${categoryId}/${fileName}`
}
export const categoriesWithFilesEndpoint = `${FLASK_PORT}/categories_with_files`
export function fetchFilesForCategoryNameEndpoint(categoryName) {
  return `${FLASK_PORT}/files/${categoryName.toLowerCase()}`
}

/* Info */

export const userInfoEndpoint = `${FLASK_PORT}/info/user`;
export const userConfigEndpoint = `${FLASK_PORT}/data/config`;

/* Messages */

export function deleteMessageByIdEndpoint(messageId) {
  return `${FLASK_PORT}/messages/${messageId}`;
}
export function fetchMessagesByCategoryEndpoint(categoryName) {
  return `${FLASK_PORT}/messages/${categoryName}`;
}


/* Pricing */

export const userBalanceEndpoint = `${FLASK_PORT}/pricing/balance`
export const updateUserBalanceEndpoint = `${FLASK_PORT}/pricing/add`
export const sessionTotalSpentEndpoint = `${FLASK_PORT}/pricing/session`