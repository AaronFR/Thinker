

export const FLASK_PORT = process.env.REACT_APP_THE_THINKER_BACKEND_URL || "http://localhost:5000";


/* Auth */

export const loginEndpoint = `${FLASK_PORT}/auth/login`;
export const registerEndpoint = `${FLASK_PORT}/auth/register`;
export const verifyEndpoint = `${FLASK_PORT}/auth/verify`
export const validateSessionEndpoint = `${FLASK_PORT}/auth/validate`;
export const refreshSessionEndpoint = `${FLASK_PORT}/auth/refresh`;
export const logoutSessionEndpoint = `${FLASK_PORT}/auth/logout`;

/* Augmentation */

export const selectPersonaEndpoint = `${FLASK_PORT}/augmentation/select_persona`;
export const selectWorkflowEndpoint = `${FLASK_PORT}/augmentation/select_workflow`;
export const selectedCategoryEndpoint = `${FLASK_PORT}/augmentation/select_category`
export const autoEngineerPromptEndpoint = `${FLASK_PORT}/augmentation/auto_engineer_prompt`;
export const questionPromptEndpoint = `${FLASK_PORT}/augmentation/question_prompt`

/* Categories */

export const categoriesEndpoint = `${FLASK_PORT}/categories`
export const categoriesWithFilesEndpoint = `${FLASK_PORT}/categories_with_files`
export const updateCategoryInstructions = `${FLASK_PORT}/category_instructions`

/* Files */

export const filesEndpoint = `${FLASK_PORT}/files`;
export function fileIdEndpoint(uuid) {
  return `${FLASK_PORT}/file/${uuid}`
}

export function filesForCategoryNameEndpoint(categoryName) {
  return `${FLASK_PORT}/files/category/${categoryName.toLowerCase()}`
}

export function fileAddressEndpoint(categoryId, fileName) {
  return `${FLASK_PORT}/file_address/${categoryId}/${fileName}`
}

/* Info */

export const userInfoEndpoint = `${FLASK_PORT}/info/user`;
export const userConfigEndpoint = `${FLASK_PORT}/info/config`;

/* Messages */

export function deleteMessageByIdEndpoint(messageId) {
  return `${FLASK_PORT}/messages/${messageId}`;
}
export function messagesForCategoryEndpoint(categoryName) {
  return `${FLASK_PORT}/messages/${categoryName}`;
}

/* Pricing */

export const userBalanceEndpoint = `${FLASK_PORT}/pricing/balance`
export const updateUserBalanceEndpoint = `${FLASK_PORT}/pricing/add`
export const sessionTotalSpentEndpoint = `${FLASK_PORT}/pricing/session`