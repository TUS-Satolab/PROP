'use strict';

// export const SERVER_URL = 'http://localhost:5004/complete';
// export const QUERY_URL = 'http://localhost:5004/task_query';
// export const GET_RESULT_URL = 'http://localhost:5004/get_result_completed';
// export const ALIGN_URL = 'http://localhost:5004/alignment';
// export const MATRIX_URL = 'http://localhost:5004/matrix';
// export const TREE_URL = 'http://localhost:5004/tree';




const arrList = require('./env.json');
const IP = String ( arrList.env[0].ip_address ) ;
const first = 'http://';
const lastComplete = ':5004/complete';
const lastQuery = ':5004/task_query';
const lastResComp = ':5004/get_result_completed';
const lastAlign = ':5004/alignment';
const lastMatrix = ':5004/matrix';
const lastTree = ':5004/tree';

export const SERVER_URL = String ( first + IP + lastComplete );
export const QUERY_URL = String ( first + IP + lastQuery );
export const GET_RESULT_URL = String ( first + IP + lastResComp );
export const ALIGN_URL = String ( first + IP + lastAlign );
export const MATRIX_URL = String ( first + IP + lastMatrix );
export const TREE_URL = String ( first + IP + lastTree );



