import { environment } from '../environments/environment';

export const VERSION = 6;

const BASE_URL = environment.baseUrl;

export const SERVER_URL = `${BASE_URL}/complete`;
export const QUERY_URL = `${BASE_URL}/task_query`;
export const GET_RESULT_URL = `${BASE_URL}/get_result_completed`;
export const ALIGN_URL = `${BASE_URL}/alignment`;
export const MATRIX_URL = `${BASE_URL}/matrix`;
export const TREE_URL = `${BASE_URL}/tree`;
export const CANCEL_URL = `${BASE_URL}/cancel_job`;
