'use strict';

var SERVER_URL_TEMP = '';
var QUERY_URL_TEMP = '';
var GET_RESULT_URL_TEMP = '';
var ALIGN_URL_TEMP = '';
var MATRIX_URL_TEMP = '';
var TREE_URL_TEMP = '';
var CANCEL_URL_TEMP = '';
const LOCALHOST_BASE_URL = 'http://localhost:5004';
const REMOTE_SERVER_BASE_URL = 'https://9nrzjbva00.execute-api.ap-northeast-1.amazonaws.com/dev';
export const VERSION = 6;

const arrList = require('./env.json');

if (String(arrList.env[1].local_flag) === '1') {
  var SERVER_URL_TEMP = `${LOCALHOST_BASE_URL}/complete`;
  var QUERY_URL_TEMP = `${LOCALHOST_BASE_URL}/task_query`;
  var GET_RESULT_URL_TEMP = `${LOCALHOST_BASE_URL}/get_result_completed`;
  var ALIGN_URL_TEMP = `${LOCALHOST_BASE_URL}/alignment`;
  var MATRIX_URL_TEMP = `${LOCALHOST_BASE_URL}/matrix`;
  var TREE_URL_TEMP = `${LOCALHOST_BASE_URL}/tree`;
  var CANCEL_URL_TEMP = `${LOCALHOST_BASE_URL}/cancel_job`;
} else {
  var SERVER_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/complete`;
  var QUERY_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/task_query`;
  var GET_RESULT_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/get_result_completed`;
  var ALIGN_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/alignment`;
  var MATRIX_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/matrix`;
  var TREE_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/tree`;
  var CANCEL_URL_TEMP = `${REMOTE_SERVER_BASE_URL}/cancel_job`;
}

export const SERVER_URL = SERVER_URL_TEMP;
export const QUERY_URL = QUERY_URL_TEMP;
export const GET_RESULT_URL = GET_RESULT_URL_TEMP;
export const ALIGN_URL = ALIGN_URL_TEMP;
export const MATRIX_URL = MATRIX_URL_TEMP;
export const TREE_URL = TREE_URL_TEMP;
export const CANCEL_URL = CANCEL_URL_TEMP;
